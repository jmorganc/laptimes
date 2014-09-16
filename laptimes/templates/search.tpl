%rebase('templates/layout.tpl', title='Racer Search')
        <div class="page-header">
            <h1>Search for a Racer</h1>
        </div>
        <div class="row">
            <div class="col-md-4">
                <div class="input-group">
                    <form class="navbar-form navbar-left" action="/search_racers" method="post">
                        <input name="racer_name" type="text" class="form-control" placeholder="Racer Name" autofocus="autofocus">&nbsp;
                        <button type="submit" class="btn btn-primary">Search</button>
                    </form>
                </div>
            </div>

            %if racers:
            <div class="col-md-8">
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
            </div>
            %end
        </div>
