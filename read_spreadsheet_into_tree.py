import org_chart_tree


def read_spreadsheet_into_tree():
    values = [['Full Name',     'Display Name', 'Title',   'Manager',       'Location',    'Timezone',            'Start Date', 'End Date', 'Full/Part-Time'],
              ['Amanda Talbot', 'Amanda',       'CEO',     '',              'New York',    'America/New_York',    'Jan 1, 2000', '', ''],
              ['Edna Barker',   'Edna',         'COO',     'Amanda Talbot', 'Los Angeles', 'America/Los_Angeles', 'Aug 1, 2010', '', '']
    ]

    if not values:
        # print('No data found.')
        # sys.exit(1)
        return None
    else:
        org_chart = org_chart_tree.OrgChart()
        id = 1

        for row in values[1:]:
            node = org_chart_tree.OrgChartNode()

            node.id = id
            id = id + 1
            if len(row) >= 1:
                node.full_name = row[0]
                if len(row) >= 2:
                    node.display_name = row[1]
                if len(row) >= 3:
                    node.title = row[2]
                if len(row) >= 4:
                    node.manager_name = row[3]
                if len(row) >= 5:
                    node.location = row[4]
                if len(row) >= 6:
                    node.timezone = row[5]
                if len(row) >= 7:
                    node.start_date = row[6]
                if len(row) >= 8:
                    node.end_date = row[7]
                if len(row) >= 9:
                    node.part_time = row[8] == '(part-time)'
                    node.occasional_time = row[8] == '(occasional)'
                    node.full_time = not node.part_time and not node.occasional_time
                node.post_read_node()
                org_chart.add_node(node)

        errors = org_chart.post_read_of_all_nodes()
        return org_chart, errors
