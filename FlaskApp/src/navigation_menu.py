import dash_bootstrap_components as dbc


nav_menu = dbc.Nav(
    [
        dbc.NavLink("Top",
                    href="/",
                    external_link=True),
        dbc.NavLink("List",
                    href="/list",
                    external_link=True),
        dbc.NavLink("OverView",
                    href="/overview",
                    external_link=True),
        dbc.DropdownMenu(
            [
                dbc.NavLink("Person",
                            href="/dashboard/person",
                            external_link=True),
                dbc.NavLink("Team",
                            href="/dashboard/team",
                            external_link=True),
                dbc.NavLink("Matching",
                            href="/dashboard/matching",
                            external_link=True),
            ],
            label="DashBoard",
            nav=True
        ),
        dbc.DropdownMenu(
            [
                dbc.NavLink("Download",
                            href="/data/download",
                            external_link=True),
                dbc.NavLink("Upload",
                            href="/data/upload",
                            external_link=True),
                dbc.NavLink("Edit",
                            href="/data/edit",
                            external_link=True),
                dbc.NavLink("Delete",
                            href="/data/delete",
                            external_link=True)
            ],
            label="Data",
            nav=True
        ),
        dbc.NavLink("Q&A",
                    href="/QA",
                    external_link=True
                    ),

    ],
    style=dict(margin="30px 0px"),
)
