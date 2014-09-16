%rebase('templates/layout.tpl', title='Profile: {0}'.format(racer['name']))
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        <script type="text/javascript">
            google.load("visualization", "1", {packages:["corechart"]});
            google.setOnLoadCallback(drawChart);
            function drawChart() {
                var data = google.visualization.arrayToDataTable([
                    ['Laps', 'Time'],
                    %i = 1
                    %for lap in laps:
                    [{{i}}, {{lap['laptime']}}],
                    %i += 1
                    %end
                ]);

                var options = {
                    title: 'Laptimes',
                    curveType: 'function',
                    legend: 'none',
                    hAxis: { title: 'Lap', ticks: {{range(1, len(laps) + 1)}} },
                    vAxis: { title: 'Time (s)' }
                };

                var chart = new google.visualization.LineChart(document.getElementById('chart_div'));

                chart.draw(data, options);
            }

            google.setOnLoadCallback(drawChart2);
            function drawChart2() {
                var data = google.visualization.arrayToDataTable([
                    ['Laps', 'Time'],
                    %i = 1
                    %for lap in laps:
                    [{{i}}, {{lap['laptime']}}],
                    %i += 1
                    %end
                ]);

                var options = {
                    title: 'Laptime Trend',
                    hAxis: {title: 'Laps'},
                    vAxis: {title: 'Time (s)'},
                    legend: 'none',
                    trendlines: { 0: {} }    // Draw a trendline for data series 0.
                };

                var chart = new google.visualization.ScatterChart(document.getElementById('trend_div'));
                chart.draw(data, options);
            }

            google.load("visualization", "1", {packages:["table"]});
            google.setOnLoadCallback(drawTable);

            function drawTable() {
                var data = new google.visualization.DataTable();
                data.addColumn('number', 'Laptime');
                data.addColumn('string', 'Datetime');
                data.addRows([
                    %for lap in laps:
                    [{{lap['laptime']}}, '{{lap['datetime']}}'],
                    %end
                ]);

                var table = new google.visualization.Table(document.getElementById('table_div'));

                table.draw(data, {showRowNumber: true});
            }
        </script>

        <h1>{{racer['name']}}</h1>

        %for key, val in racer.iteritems():
        {{key}}: {{val}}<br/>
        %end

        <br/>

        <div id="table_div"></div>
        <div id="chart_div" style="width: 900px; height: 500px;"></div>
        <div id="trend_div" style="width: 900px; height: 500px;"></div>
