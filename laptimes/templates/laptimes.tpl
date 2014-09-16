%rebase('templates/layout.tpl', title='Top {0}'.format(top_num))
        <div class="page-header">
            <h1>Top {{top_num}} Laptimes</h1>
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
                <td>weather</td>
            </tr>
            %   i += 1
            %end
        </table>