%rebase('templates/layout.tpl', title='Profile: {0}'.format(racer['name']))
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        <script type="text/javascript">
            google.load("visualization", "1", {packages:["corechart"]});
            google.setOnLoadCallback(drawChart);
            function drawChart() {
            var data = google.visualization.arrayToDataTable([
                ['Lap', 'Time'],
                %i = 1
                %for lap in laps:
                [{{i}}, {{lap['laptime']}}],
                %i += 1
                %end
            ]);

            var options = {
                title: 'Laptimes',
                curveType: 'function',
                legend: { position: 'bottom' },
                hAxis: { title: 'Lap', ticks: {{range(1, len(laps) + 1)}} },
                vAxis: { title: 'Time (s)' }
            };

            var chart = new google.visualization.LineChart(document.getElementById('chart_div'));

            chart.draw(data, options);
            }
        </script>

        <h1>{{racer['name']}}</h1>

        %for key, val in racer.iteritems():
        {{key}}: {{val}}<br/>
        %end

        <br/>

        %for lap in laps:
        %   for key, val in lap.iteritems():
        {{key}}: {{val}}<br/>
        %   end
        %end

        <div id="chart_div" style="width: 900px; height: 500px;"></div>