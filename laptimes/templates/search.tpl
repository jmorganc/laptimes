%rebase('templates/layout.tpl', title='Racer Search')
        <div class="page-header">
            <h1>Search for a Racer</h1>
        </div>
		<div class="input-group">
			<form class="navbar-form navbar-left" action="/search_racers" method="post">
				<input name="racer_name" type="text" class="form-control" placeholder="Racer Name">
				<button type="submit" class="btn btn-default">Search</button>
			</form>
		</div>
