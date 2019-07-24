
class ApiHandler:
    def __init__(self, modules):
        self.modules = modules
    #TODO Modify for Yellyfish
    def index(self):
        return '''
        <html><head><title>QuallenControl</title></head>
        <body>
        <button onclick="call('left_eye')">Zwinker Links</button>
        <button onclick="call('right_eye')">Zwinker Rechts</button>
        <button onclick="call('strobo')">Strobo</button>        
        <input type="color" id="color"/>
        <label><input type="checkbox" id="color_loop" onclick="handleClick(this)"/>Color loop</label>
        <label><input type="checkbox" id="music" onclick="handleMusic(this)" checked/>Music</label>
        <input type="range" min=0 max=4 step=0.02 id="range"/>
        <p id="result">Press a button</p>
        <script type="text/javascript">
        var range = document.getElementById("range");
        range.addEventListener("change", function(event) {
        if(document.getElementById("music").value)
            call('gill_control', event.target.value);

        }, false);
        function handleClick(cb) {
        call('color_loop', cb.checked ? 1 : 0);
        }
        function handleMusic(cb) {
        if(cb.checked)
            call('gill_control', -1);
        else
            call('gill_control', document.getElementById("range").value);
        }
        function call(operation, val) {
        var xhttp = new XMLHttpRequest();
        document.getElementById("result").innerHTML = "calling";
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
            document.getElementById("result").innerHTML = "done";
            }
        };
        var path = "/api?operation=" + operation;
        if(val) {
         path += "&value=" + val;
        }
        xhttp.open("GET", path, true);
        xhttp.send();
        }
        var cp = document.getElementById('color');
        cp.addEventListener("change", function(event) {
        call('color', event.target.value.substr(1));
        }, false);

        </script>
        </body>
        </html>
        '''

    def get(self, api_request):
        print(api_request)
        operation =  api_request['query_params'].get('operation', 'index')
        """
        if 'left_eye' == operation:
            self.modules['left_eye'].blink()
        elif 'right_eye' == operation:
            self.modules['right_eye'].blink()
        elif 'strobo' == operation:
            self.modules['gills'].setmode('strobo')
        elif 'color_loop'  == operation:
            value = int(api_request['query_params']['value']) == 1
            self.modules['left_eye'].color_loop = value
            self.modules['right_eye'].color_loop = value
        elif 'color' == operation:
            html_color = api_request['query_params']['value']
            value = tuple(int(html_color[i:i+2], 16) for i in (0, 2, 4))
            self.modules['left_eye'].color = value
            self.modules['right_eye'].color = value
            self.modules['left_eye'].all_pixels()
            self.modules['right_eye'].all_pixels()
        elif 'gill_control'  == operation:
            value = float(api_request['query_params']['value'])
            if value == -1:
                self.modules['gills'].setmode('normal')
            else:
                self.modules['gills'].setmode('color', value)
        """
        if operation == "strobo":
            self.modules['qualle'].setmode('strobo')
        elif operation == 'index':
            return self.index()
