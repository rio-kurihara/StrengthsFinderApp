import dash_bootstrap_components as dbc


nav_menu = dbc.Nav(
    [
        dbc.NavLink("Top",
                    href="/top",
                    external_link=True),
        dbc.NavLink("OverView",
                    href="/dashboard/overview",
                    external_link=True),
        dbc.DropdownMenu(
            [
                dbc.NavLink("Group",
                            href="/dashboard/group",
                            external_link=True),
                dbc.NavLink("Person",
                            href="/dashboard/person",
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
                            href="/download",
                            external_link=True),
                dbc.NavLink("Upload",
                            href="/upload",
                            external_link=True),
                dbc.NavLink("Edit",
                            href="/edit",
                            external_link=True,
                            disabled=True),
            ],
            label="Data",
            nav=True
        ),
        dbc.NavLink("Help",
                    href="/help",
                    external_link=True
                    ),

    ],
    style=dict(margin="30px 0px"),
)
