%rebase('templates/layout.tpl', title='Top {0}'.format(top_num), active_home='class="active"')
        <script src="/js/bootstrap-datepicker.js"></script>
        <script type="text/javascript">
            $(document).ready(function() {
                $('[data-toggle=popover]').popover({html:true})
                $('#datepicker-container .input-group.date').datepicker({
                        format: "yyyy-mm-dd",
                        todayHighlight: true
                    })
                    .on('changeDate', function(e) {
                        date_split = e.date.toLocaleDateString().split('/')
                        url = '/laptimes/date/' + date_split[2] + '/' + date_split[0] + '/' + date_split[1];
                        window.location.href = url;
                    });
            });
        </script>
        <div class="page-header">
            %if top_num > 0:
            <h1>Top {{top_num}} Laptimes</h1>
            %else:
            <h1>Top Laptimes</h1>
            %end
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
                        %if date == (0, 0, 0):
                        %   value_date = current_date
                        %else:
                        %   year, month, day = date[0], date[1], date[2]
                        %   if month < 10:
                        %       month = '0{0}'.format(month)
                        %   end
                        %   if day < 10:
                        %       day = '0{0}'.format(day)
                        %   end
                        %   value_date = '{0}-{1}-{2}'.format(date[0], month, day)
                        %end
                        <input type="text" class="form-control" value="{{value_date}}"><span class="input-group-addon"><i class="glyphicon glyphicon-th"></i></span>
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
            %   datacontent_str = ''
            %   if weather_data[row['id']]:
            %      datacontent_str = 'Wind from the {0} at {1} mph'.format(weather_data[row['id']]['wind_dir'], weather_data[row['id']]['wind_mph'])
            %   end
            %   for key, value in weather_data[row['id']].iteritems():
            %      if key in ['Weather', 'Temperature', 'wind_dir', 'wind_mph']:
            %         continue
            %      end
            %      datacontent_str += '<div style="padding: 3px 0px;">{0}: {1}</div>'.format(key, str(value))
            %   end
            <tr>
                <td>{{i}}</td>
                <td><a href="/racer/{{row['id']}}">{{row['name']}}</a></td>
                <td>{{row['laptime']}}</td>
                <td>{{row['datetime']}}</td>
                <td>
                    %if weather_data[row['id']]:
                    <a href="javascript:void(0);" tabindex="0" data-toggle="popover" data-trigger="focus" title="{{str(weather_data[row['id']]['Temperature'])}}&deg;F and {{weather_data[row['id']]['Weather']}}" data-content="{{datacontent_str}}">
                        {{weather_data[row['id']]['Temperature']}}&deg;F and {{weather_data[row['id']]['Weather']}}
                    </a>
                    %else:
                    <span style="color: #999;">No data</span>
                    %end
                </td>
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
