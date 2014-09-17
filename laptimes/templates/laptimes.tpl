%rebase('templates/layout.tpl', title='Top {0}'.format(top_num), active_home='class="active"')
        <script src="/js/bootstrap-datepicker.js"></script>
        <script type="text/javascript">
            $(document).ready(function() {
                $('#datepicker-container .input-group.date').datepicker({
                        format: "yyyy-mm-dd"
                    })
                    .on('changeDate', function(e) {
                        console.log(e.date);
                        console.log(e.date.toLocaleDateString());
                        console.log(e.date.parse());
                        //window.location.href = '/laptimes/date/' + e.date;
                    });
            });
        </script>
        <div class="page-header">
            <h1>Top {{top_num}} Laptimes</h1>
        </div>

        %disabled_10 = ''
        %disabled_25 = ''
        %disabled_50 = ''
        %disabled_100 = ''

        %if top_num == 10:
        %   disabled_10 = ' disabled'
        %end
        %if top_num == 25:
        %   disabled_25 = ' disabled'
        %end
        %if top_num == 50:
        %   disabled_50 = ' disabled'
        %end
        %if top_num == 100:
        %   disabled_100 = ' disabled'
        %end

        <div class="row">
            <div class="col-md-4">
                <h2 style="margin-top: 0px;">
                    %if top_num > 0:
                    Average laptime: {{average}}
                    %end
                </h2>
            </div>
        </div>
        </br>

        <div class="row">
            <div class="col-md-1">
                <a href="/" class="btn btn-primary" role="button">All time</a>
            </div>
            <div class="col-md-2">
                <div id="datepicker-container">
                    <div class="input-group date">
                        <input type="text" class="form-control"><span class="input-group-addon"><i class="glyphicon glyphicon-th"></i></span>
                    </div>
                </div>
            </div>
            <div class="col-md-5"></div>
            <div class="col-md-4" style="text-align: right;">
                %date_url = ''
                %if date[0] > 0:
                %   date_url = 'date/{0}/'.format(date[0])
                %end
                %if date[1] > 0:
                %   date_url = 'date/{0}/{1}/'.format(date[0], date[1])
                %end
                %if date[2] > 0:
                %   date_url = 'date/{0}/{1}/{2}/'.format(date[0], date[1], date[2])
                %end
                <a href="/laptimes/{{date_url}}top/10" class="btn btn-primary{{disabled_10}}" role="button">Top 10</a>
                <a href="/laptimes/{{date_url}}top/25" class="btn btn-primary{{disabled_25}}" role="button">Top 25</a>
                <a href="/laptimes/{{date_url}}top/50" class="btn btn-primary{{disabled_50}}" role="button">Top 50</a>
                <a href="/laptimes/{{date_url}}top/100" class="btn btn-primary{{disabled_100}}" role="button">Top 100</a>
            </div>
        </div>
        <br/>

        <table class="table table-striped">
            <tr>
                <th>Rank</th>
                <th>Racer Name</th>
                <th>Laptime</th>
                <th>Date and Time</th>
                <th>Conditions</th>
            </tr>
            %i = 1
            %for row in rows:
            <tr>
                <td>{{i}}</td>
                <td><a href="/racer/{{row['id']}}">{{row['name']}}</a></td>
                <td>{{row['laptime']}}</td>
                <td>{{row['datetime']}}</td>
                <td>{{weather_summary[row['id']]['weather']}}</td>
            </tr>
            %   i += 1
            %end
        </table>

        <div class="row">
            <div class="col-md-12" style="text-align: center;">
                %if top_num == 0:
                <h3>No results found</h3>
                %end
            </div>
        </div>
