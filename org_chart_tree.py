import sys
import datetime
import pytz

MAJOR_ROW_HEIGHT = 20
MINOR_ROW_HEIGHT = 5
MAJOR_COLUMN_GUTTER = 10
CELL_HEIGHT = 50
CELL_WIDTH = 100
START_END_WIDTH = 40
START_END_HEIGHT = 16
START_END_ARROW = 5
START_END_OUTDENT = -8
START_END_UPDENT = -6
TOP_MARGIN = 10
BOTTOM_MARGIN = 10
LEFT_MARGIN = 10
RIGHT_MARGIN = 20


class OrgChartNode:
    def __init__(self):
        self.id = None
        self.parent = None
        self.children = None
        self.full_name = None
        self.display_name = None
        self.title = None
        self.manager_name = None
        self.location = None
        self.timezone = None
        self.start_date = None
        self.end_date = None
        self.team_lead = False
        self.full_time = True
        self.part_time = False
        self.occasional_time = False
        self.hired_before = []
        self.height = None
        self.width = None
        self.x = None
        self.y = None

    def post_read_node(self):
        if not self.display_name:
            if self.full_name[0] == '(':
                self.display_name = None
            else:
                self.display_name = self.full_name
        if not self.start_date:
            self.start_date = None
        if not self.end_date:
            self.end_date = None

    def determine_y_position(self, row_y_position):
        self.y = row_y_position
        if self.children is not None:
            if self.team_lead:
                y = row_y_position + CELL_HEIGHT + MAJOR_ROW_HEIGHT
                for each in self.children:
                    each.y = y
                    y += CELL_HEIGHT + MINOR_ROW_HEIGHT
            else:
                for each in self.children:
                    each.determine_y_position(row_y_position + CELL_HEIGHT + MAJOR_ROW_HEIGHT)

    def determine_x_position(self, offset):
        width = self.get_width()
        self.x = int(width / 2) + offset
        if self.children is not None:
            if self.team_lead:
                for each in self.children:
                    each.x = self.x
            else:
                for each in self.children:
                    each.determine_x_position(offset)
                    offset = offset + each.get_width() + MAJOR_COLUMN_GUTTER

    def get_width(self):
        if self.width is not None:
            return self.width
        if self.children is None:
            width = CELL_WIDTH
        else:
            if self.team_lead:
                width = CELL_WIDTH
            else:
                width = 0
                for each in self.children:
                    width += each.get_width()
                    width += MAJOR_COLUMN_GUTTER
                width -= MAJOR_COLUMN_GUTTER
        self.width = width
        return self.width

    def get_height(self):
        if self.height is not None:
            return self.height
        if self.children is None:
            height = self.y + CELL_HEIGHT
        else:
            height = 0
            for each in self.children:
                h = each.get_height()
                if h > height:
                    height = h
        self.height = height
        return self.height

    def generate_all_svg(self, fp):
        if self.children is not None:
            self.generate_connector_svg(fp)
        self.generate_svg(fp)
        if self.children is not None:
            for each in self.children:
                each.generate_all_svg(fp)

    def generate_connector_svg(self, fp):
        fp.write('<line x1="%d" y1="%d" x2="%d" y2="%d" style="stroke:#888;stroke-width:1"/>'
                 % (self.x, int(self.y + (CELL_HEIGHT)), self.x, int(self.y + CELL_HEIGHT + (MAJOR_ROW_HEIGHT / 2))))
        min_x = sys.maxsize
        max_x = 0
        for each in self.children:
            x = each.x
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            fp.write('<line x1="%d" y1="%d" x2="%d" y2="%d" style="stroke:#888;stroke-width:1"/>'
                 % (each.x, int(each.y), each.x, int(each.y - (MAJOR_ROW_HEIGHT / 2))))
        y = int(self.y + CELL_HEIGHT + (MAJOR_ROW_HEIGHT / 2))
        fp.write('<line x1="%d" y1="%d" x2="%d" y2="%d" style="stroke:#888;stroke-width:1"/>'
             % (min_x, y, max_x, y))

    def generate_svg(self, fp):
        if self.display_name is None:
            return
        fp.write('<g id="p%s" transform="translate(%d,%d)">' % (self.id, int(self.x - (CELL_WIDTH / 2)), self.y))
        if self.full_time:
            stroke_color = '#888'
        else:
            stroke_color = '#ccc'
        fp.write('<rect width="%d" height="%d" style="fill:#F0FFFF;stroke:%s;stroke-width:2" />'
                 % (CELL_WIDTH, CELL_HEIGHT, stroke_color))
        if self.timezone:
            fp.write('<text x="90" y="10" alignment-baseline="middle" font-size="13" stroke-width="0" stroke="#000" fill="#666" text-anchor="middle">%s</text>'
                % self.timezone)
        fp.write('<text x="%d" y="%d" alignment-baseline="middle" font-size="18" stroke-width="0" stroke="#000" text-anchor="middle">%s</text>'
                 % (int(CELL_WIDTH / 2), 18, self.display_name))
        fp.write('<text x="%d" y="%d" alignment-baseline="middle" font-size="12" stroke-width="0" stroke="#000" text-anchor="middle">%s</text>'
                 % (int(CELL_WIDTH / 2), 39, self.title))
        if self.start_date:
            self.generate_svg_start_date(fp)
        if self.end_date:
            self.generate_svg_end_date(fp)
        fp.write('</g>')
        if self.hired_before:
            fp.write('<script>')
            fp.write('$("#p%s").mouseenter(function() {' % self.id)
            for eachid in self.hired_before:
                fp.write('$("#p%s").css("opacity","0.4");' % eachid)
            fp.write('}).mouseleave(function() {')
            for eachid in self.hired_before:
               fp.write('$("#p%s").css("opacity","");' % eachid)
            fp.write('});')
            fp.write('</script>')

    def generate_svg_start_date(self, fp):
        sd = datetime.datetime.strptime(self.start_date, "%b %d, %Y")
        if sd > datetime.datetime.today():
            fp.write('<g transform="translate(%d,%d)">' % (START_END_OUTDENT, CELL_HEIGHT - (START_END_HEIGHT / 2) + START_END_UPDENT))
            x1 = 0
            x2 = (START_END_ARROW)
            x3 = START_END_WIDTH
            x4 = START_END_WIDTH + (START_END_ARROW)
            y1 = 0
            y2 = (START_END_HEIGHT / 2)
            y3 = START_END_HEIGHT
            fp.write('<polygon points="%d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d" style="fill:#88FF88;stroke:#666;stroke-width:1"/>'
                     % (x1,y1, x3,y1, x4,y2, x3,y3, x1,y3, x2,y2, x1,y1) )
            fp.write(
                '<text x="%d" y="%d" alignment-baseline="middle" font-size="9" stroke-width="0" stroke="#000" text-anchor="middle">%s</text>'
                % (int(START_END_WIDTH / 2) + (START_END_ARROW * 0.6), (START_END_HEIGHT / 2),
                   datetime.datetime.strftime(sd, "%b %d")))
            fp.write('</g>')

    def generate_svg_end_date(self, fp):
        ed = datetime.datetime.strptime(self.end_date, "%b %d, %Y")
        if ed >= datetime.datetime.today():
            fp.write('<g transform="translate(%d,%d)">' % (CELL_WIDTH - START_END_WIDTH , CELL_HEIGHT - (START_END_HEIGHT / 2) + START_END_UPDENT))
            x1 = 0
            x2 = START_END_ARROW
            x3 = START_END_WIDTH
            x4 = START_END_WIDTH + START_END_ARROW
            y1 = 0
            y2 = (START_END_HEIGHT / 2)
            y3 = START_END_HEIGHT
            fp.write('<polygon points="%d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d" style="fill:#FFaaaa;stroke:#666;stroke-width:1"/>'
                     % (x1,y1, x3,y1, x4,y2, x3,y3, x1,y3, x2,y2, x1,y1) )
            fp.write(
                '<text x="%d" y="%d" alignment-baseline="middle" font-size="9" stroke-width="0" stroke="#000" text-anchor="middle">%s</text>'
                % (int(START_END_WIDTH / 2) + (START_END_ARROW * 0.6), (START_END_HEIGHT / 2),
                   datetime.datetime.strftime(ed, "%b %d")))
            fp.write('</g>')

    def annotate_timezones(self, browser_timezone):
        if self.timezone == browser_timezone:
            self.timezone = ''
        else:
            local_timestamp = datetime.datetime.now()
            browser_timestamp = pytz.timezone(browser_timezone).localize(local_timestamp).astimezone(pytz.utc)
            my_timestamp = pytz.timezone(self.timezone).localize(local_timestamp).astimezone(pytz.utc)
            delta = browser_timestamp - my_timestamp
            self.timezone = round(delta.total_seconds() / 60.0 / 60.0)
            if self.timezone > 0:
                self.timezone = '+' + str(self.timezone)
            else:
                self.timezone = str(self.timezone)

        if self.children is not None:
            for each in self.children:
                each.annotate_timezones(browser_timezone)

    def compute_hired_before_lists(self, all_node_id_and_dates):
        if self.start_date:
            ssd = datetime.datetime.strptime(self.start_date, "%b %d, %Y")
            self.hired_before = [each[0] for each in all_node_id_and_dates if each[1] > ssd]
        if self.children is not None:
            for each in self.children:
                each.compute_hired_before_lists(all_node_id_and_dates)


class OrgChart:
    def __init__(self):
        self.all_nodes = {}
        self.top_node = None

    def add_node(self, node):
        self.all_nodes[node.full_name] = node

    def post_read_of_all_nodes(self):
        errors = []
        self.remove_terminated_nodes()
        self.remove_occasional_nodes()
        self.connect_parents_and_children(errors)
        self.find_team_lead_nodes()
        self.sort_children()
        self.verify_dates(errors)
        self.verify_timezones(errors)
        return errors

    def verify_timezones(self, errors):
        for node in self.all_nodes.values():
            if node.timezone:
                try:
                    _ = pytz.timezone(node.timezone)
                except:
                    errors.append("%s does not have a valid timezone (%s is not a pytz timezone)"
                                  % (node.full_name, node.timezone))
                    node.timezone = 'America/New_York'
            else:
                errors.append("%s does not have a timezone" % node.full_name)
                node.timezone = 'America/New_York'

    def verify_dates(self, errors):
        for node in self.all_nodes.values():
            # has start date?
            if not node.start_date:
                errors.append("%s has no start date" % node.full_name)
                node.start_date = datetime.date.today().strftime("%b %d, %Y")
            else:
                # start date parseable?
                try:
                    d = datetime.datetime.strptime(node.start_date, "%b %d, %Y")
                except:
                    errors.append("%s start date (%s) is not valid MMM DD, YYYY format"
                                  % (node.full_name, node.start_date))
                    node.start_date = datetime.date.today().strftime("%b %d, %Y")
            # end date parseable?
            if node.end_date:
                try:
                    _ = datetime.datetime.strptime(node.end_date, "%b %d, %Y")
                except:
                    errors.append("%s end date (%s) is not valid MMM DD, YYYY format"
                                  % (node.full_name, node.end_date))
                    node.end_date = None

    def sort_children(self):
        for node in self.all_nodes.values():
            # sort the children
            if node.children is not None:
                node.children = sorted(node.children, key=lambda x: str.lower(x.display_name))

    def find_team_lead_nodes(self):
        for node in self.all_nodes.values():
            # determine which are team_leads
            if not node.children:
                node.team_lead = False
            else:
                children_have_children = False
                for each in node.children:
                    if each.children:
                        children_have_children = True
                if children_have_children:
                    node.team_lead = False
                else:
                    node.team_lead = True

    def connect_parents_and_children(self, errors):
        self.top_node = None
        for node in self.all_nodes.values():
            # make the parent and child links
            if node.manager_name not in self.all_nodes:
                if node.manager_name == "":
                    if self.top_node:
                        errors.append("%s does not have a manager" % node.full_name)
                    else:
                        self.top_node = node
                else:
                    errors.append("%s lists a manager (%s) who does not exist; maybe misspelled?"
                                  % (node.full_name, node.manager_name))
            else:
                node.parent = self.all_nodes[node.manager_name]
                if node.parent.children is None:
                    node.parent.children = []
                node.parent.children.append(node)

    def remove_terminated_nodes(self):
        removes = []
        for node in self.all_nodes.values():
            # remove any terminated rows
            if node.end_date is not None:
                try:
                    ed = datetime.datetime.strptime(node.end_date, "%b %d, %Y")
                    if ed < datetime.datetime.today():
                        removes.append(node)
                except:
                    pass # the error will be reported later
        if len(removes):
            for node in removes:
                del self.all_nodes[node.full_name]

    def remove_occasional_nodes(self):
        removes = []
        for node in self.all_nodes.values():
            # remove any rows with type "occasional"
            if node.occasional_time:
                removes.append(node)
        if len(removes):
            for node in removes:
                del self.all_nodes[node.full_name]

    def determine_y_positions(self):
        self.top_node.determine_y_position(TOP_MARGIN)

    def determine_x_positions(self):
        self.top_node.determine_x_position(LEFT_MARGIN)

    def get_max_dimensions(self):
        return (self.top_node.get_width() + RIGHT_MARGIN), (self.top_node.get_height() + BOTTOM_MARGIN)

    def generate_svg(self, fp):
        self.top_node.generate_all_svg(fp)

    def annotate_timezones(self, browser_timezone):
        self.top_node.annotate_timezones(browser_timezone)

    def compute_hired_before_lists(self):
        self.top_node.compute_hired_before_lists([(each.id, datetime.datetime.strptime(each.start_date, "%b %d, %Y")) for each in self.all_nodes.values()])