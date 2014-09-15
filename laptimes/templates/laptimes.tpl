%rebase('templates/layout.tpl', title='Top {0}'.format(top_num))
        <h1>Top {{top_num}} Laptimes</h1>
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
                %for col in row:
                <td>{{col}}</td>
                %end
                <td>weather</td>
            </tr>
            %   i += 1
            %end
        </table>