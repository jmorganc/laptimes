%rebase('templates/layout.tpl', title='Search Results')
        <h1>Search Results</h1>

        %for racer in racers:
        {{racer}}<br/>
        %end
