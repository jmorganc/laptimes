%rebase('templates/layout.tpl', title='Live Timing', active_home='class="active"')
        <script src="/js/bootstrap-datepicker.js"></script>
        <script type="text/javascript">
            $(document).ready(function() {
                        window.location.href = url;
                    });
        </script>
        <div class="page-header">
            <h1>Live Timing</h1>
        </div>

        <table class="table table-striped">
            <tr>
                <th>Position</th>
                <th>Kart</th>
                <th>Racer</th>
                <th>Lap Time</th>
                <th>Best Lap Time</th>
                <th>Laps</th>
                <th>Gap</th>
            </tr>
            %for racer in racers:
            <tr>
                <td>{{racer[0]}}</td>
                <td>{{racer[1]}}</td>
                <td>{{racer[2]}}</td>
                <td>{{racer[3]}}</td>
                <td>{{racer[4]}}</td>
                <td>{{racer[5]}}</td>
                <td>{{racer[6]}}</td>
            </tr>
            %end
        </table>

        <div class="row">
            <div class="col-md-12" style="text-align: center;">
                %if not racers:
                <h3>Hmm... No race appears to be happening</h3>
                %end
            </div>
        </div>
