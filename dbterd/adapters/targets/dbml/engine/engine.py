from dbterd.adapters.targets.dbml.engine.meta import Ref, Table, Column
from sql_metadata import Parser


def parse(manifest, **kwargs):
    # Parse Table
    tables = get_tables(manifest)
    # -- apply selection
    select_rule = (kwargs.get("select") or "").lower().split(":")
    if select_rule[-1].startswith("schema"):
        select_rule = select_rule[1]
        tables = [
            x
            for x in tables
            if x.schema.startswith(select_rule)  # --select schema:analytics
            or f"{x.database}.{x.schema}".startswith(
                select_rule
            )  # --select schema:db.analytics
        ]
    else:
        select_rule = select_rule[-1] # only take care of name
        tables = [x for x in tables if x.name.startswith(select_rule)]

    # -- apply exclusion (take care of name only)
    tables = [
        x
        for x in tables
        if kwargs.get("exclude") is None or not x.name.startswith(kwargs.get("exclude"))
    ]

    # Parse Rel
    relationships = get_relationships(manifest)
    table_names = [x.name for x in tables]
    relationships = [
        x
        for x in relationships
        if x.table_map[0] in table_names or x.table_map[1] in table_names
    ]

    # Build DBML content
    dbml = "//Tables (based on the selection criteria)\n"
    for table in tables:
        dbml += """Table \"{table}\"{{\n{columns}\n}}\n""".format(
            table=table.name,
            columns="\n".join([f'    "{x.name}" {x.data_type}' for x in table.columns]),
        )

    dbml += "//Rels (based on the DBT Relationship Tests)\n"
    for rel in relationships:
        dbml += f"""Ref: \"{rel.table_map[1]}\".\"{rel.column_map[1]}\" > \"{rel.table_map[0]}\".\"{rel.column_map[0]}\"\n"""

    return dbml


def get_tables(manifest):
    tables = [
        Table(
            name=x,
            raw_sql=get_compiled_sql(manifest.nodes[x]),
            database=manifest.nodes[x].database.lower(),
            schema=manifest.nodes[x].schema_.lower(),
            columns=[],
        )
        for x in manifest.nodes
        if x.startswith("model")
    ]
    for table in tables:
        parser = Parser(table.raw_sql)
        try:
            column_names = parser.columns_aliases_names
        except:
            pass

        if column_names:
            for column in column_names:
                table.columns.append(
                    Column(
                        name=column,
                    )
                )
        else:
            table.columns.append(
                Column(
                    name="(*)",
                )
            )

    return tables


def get_relationships(manifest):
    return [
        Ref(
            name=x,
            table_map=manifest.parent_map[x],
            column_map=[
                manifest.nodes[x].test_metadata.kwargs.get("field", "unknown"),
                manifest.nodes[x].test_metadata.kwargs.get("column_name", "unknown"),
            ],
        )
        for x in manifest.nodes
        if x.startswith("test") and "relationship" in x.lower()
    ]


def get_compiled_sql(manifest_node):
    if hasattr(manifest_node, "compiled_sql"):  # up to v6
        return manifest_node.compiled_sql

    if hasattr(manifest_node, "compiled_code"):  # from v7
        return manifest_node.compiled_code

    if hasattr(
        manifest_node, "columns"
    ):  # nodes having no compiled but just list of columns
        return """select 
            {columns}
        from {table}
        """.format(
            columns="\n".join(
                [
                    f"{x} as {manifest_node.columns[x].data_type or 'varchar'},"
                    for x in manifest_node.columns
                ]
            ),
            table=f"{manifest_node.database}.{manifest_node.schema}.undefined",
        )

    return manifest_node.raw_sql  # fallback to raw dbt code
