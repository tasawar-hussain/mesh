# Mesh

<h3>Setup Instructions</h3>
<ol>
  <li>Git pull repo in a directory</li>
  <li>Go to directory “cd mesh”</li>
  <li>Run command “pipenv shell” - you should have a piping pre-installed This will run a venv shell for you — this env should have python 3.8+</li>
  <li>First time?
    <ul>
      <li>Run command “pipenv lock” — to lock all dependencies and create a Pipfile.lock</li>
      <li>Run command “pipenv install --dev” — this should say “Installing dependencies from Pipfile.lock”</li>
    </ul>
  </li>
  <li>Already has a setup and taking a new pull?</li>
    <ul>
      <li>Run command “pipenv update” — records the new requirements to the Pipfile.lock file and installs the missing dependencies on the Python interpreter.</li>
    </ul>
  <li>Create a .env file with contents</li>
  <li>Create a service_account.json  file with contents</li>
  <li>Create a curl_command_for_slack_contacts.txt file with contents</li>
  <li>In root run command “python main.py”  to run application</li>
  <li> When done working deactivate your venv by running these two commands:
    <ul>
      <li>“deactivate”</li>
      <li>“exit”</li>
    </ul>
  </li>
</ol>
