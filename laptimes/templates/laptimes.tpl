%rebase('templates/layout.tpl', title='Top {0}'.format(top_num), active_home='class="active"')
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
                <h2 style="margin-top: 0px;">Average laptime: {{average}}</h2>
            </div>
            <div class="col-md-4"></div>
            <div class="col-md-4" style="text-align: right;">
                <a href="/laptimes/top/10" class="btn btn-primary{{disabled_10}}" role="button">Top 10</a>
                <a href="/laptimes/top/25" class="btn btn-primary{{disabled_25}}" role="button">Top 25</a>
                <a href="/laptimes/top/50" class="btn btn-primary{{disabled_50}}" role="button">Top 50</a>
                <a href="/laptimes/top/100" class="btn btn-primary{{disabled_100}}" role="button">Top 100</a>
            </div>
        </div>

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
