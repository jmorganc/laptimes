%rebase('templates/layout.tpl', title='Profile: {0}'.format(racer['name']))
        <h1>{{racer['name']}}</h1>

        %for key, val in racer.iteritems():
        {{key}}: {{val}}<br/>
        %end
