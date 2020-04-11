
# [START gae_python37_app]
from flask import Flask, request
from google.oauth2 import id_token
from google.auth.transport import requests
import read_spreadsheet_into_tree
from contextlib import closing
from io import StringIO

app = Flask(__name__)


@app.route('/orgchart', methods=['POST'])
def orgchart_page():
    timezone = request.form['timezone']

    org_chart, errors = read_spreadsheet_into_tree.read_spreadsheet_into_tree()
    org_chart.determine_y_positions()
    org_chart.determine_x_positions()
    dims = org_chart.get_max_dimensions()

    org_chart.annotate_timezones(timezone)
    org_chart.compute_hired_before_lists()

    with closing(StringIO()) as sio:
        sio.write("<svg width='%s' height='%s'>\n" % dims)
        org_chart.generate_svg(sio)
        sio.write("</svg>\n")
        if errors:
            sio.write("<div style='color:red;font-size:18pt;'><ul>")
            for each in errors:
                sio.write("<li>%s</li>" % each)
            sio.write("</ul></div>")
        return sio.getvalue()


@app.route('/')
def main_page():
    return """
<html lang="en">
  <head>
    <script src="https://apis.google.com/js/platform.js" async defer></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <title>Hello World Example</title>
  </head>
  <body>
  <div id="post-data"></div>
  </div>
  <p>branch 3</p>
  <script>
  $(document).ready(function () {
        $( "#post-data" ).html( "<img src='static/loading-gears-animation-10.gif'/>" );
        
        $.post( "orgchart", 
            { 
              timezone: Intl.DateTimeFormat().resolvedOptions().timeZone },
            function( data ) {
                if( data.startsWith('Not') ) {
                    $( "#post-data" ).html( '<div style="font-size:140%;color:red">401 Not Authorized</div>' +
                                            '<div>' + data + '</div>' );
                } else {
                    $( "#post-data" ).html( data );
                }
        });
      });
</script>
</body>
</html>
"""

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='0.0.0.0', port=8080, debug=True)
# [END gae_python37_app]
