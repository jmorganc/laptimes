%rebase('templates/layout.tpl', title='Search Results')
        <h1>Search Results</h1>
		<table class="table table-striped">
            <tr>
                <th>Racer Name</th>
                <th>Date Created</th>
            </tr>
            %for racer in racers:
            <tr>
                <td><a href="/racer/{{racer['id']}}">{{racer['name']}}</a></td>
                <td>{{racer['created']}}</td>
            </tr>
            %end
        </table>
