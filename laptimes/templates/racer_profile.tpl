%rebase('templates/layout.tpl', title='Profile: {0}'.format(racer['racer_name']))
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
                data.addColumn('number', 'Kart');
                data.addColumn('number', 'Lap');
                data.addColumn('number', 'Heat');
                data.addColumn('string', 'Datetime');
                data.addColumn('number', 'Temp');
                data.addRows([
                    %for lap in laps:
                    [
                        {{lap['laptime']}},
                        {{lap['kart_id']}},
                        {{lap['lap_number']}},
                        {{lap['race_id']}},
                        '{{lap['datetime']}}',
                        0
                    ],
                    %end
                ]);

                var table = new google.visualization.Table(document.getElementById('table_div'));

                table.draw(data, {showRowNumber: true});
            }
        </script>
        <script type="text/javascript">
            $('#karts').change(function() {
                console.log('test');
                //url = '#/' + $(this).option.val();
                //alert(url)
                //window.location.href = url;
            });
            // $('select').on('change', function() {
            //     alert( this.value ); // or $(this).val()
            // });
            // function test() {
            //     alert($('#karts').find(':selected').text());
            // }
        </script>

        <div class="page-header">
            <h1>{{racer['racer_name']}} <small>created: {{racer['created']}}</small></h1>
        </div>

        <div class="row">
            <div class="col-md-1">
                <select id="karts" class="form-control">
                    <option value="-1">All</option>
                    %for kart in karts:
                    <option value="{{kart['kart_id']}}">{{kart['kart_id']}}</option>
                    %end
                </select>
            </div>
        </div>

        <br/>

        <div class="row">
            <div id="table_div" class="col-md-6"></div>
            <div class="col-md-6">
                <div class="row">
                    <div class="col-md-12" style="text-align: center;">
                        <img style="border: 1px solid #999;" src="http://71.170.117.91/CustomerPictures/{{racer['id']}}.jpg" />
                    </div>
                </div>
                <br/>
                <div class="row">
                    <div class="col-md-12">
                        <div id="chart_div" style="width: 100%; height: 250px;" class="col-md-12"></div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-12">
                        <div id="trend_div" style="width: 100%; height: 250px;" class="col-md-12"></div>
                    </div>
                </div>
            </div>

        </div>
