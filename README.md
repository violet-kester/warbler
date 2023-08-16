<!-- header -->

<div align='center'>
    <img src='/static/images/warbler-logo.png' width='75px' alt='Logo'>
  <h1>Warbler</h1>
  <p>
    <i>A full-stack twitter clone application.</i>
  </p>
  <p>
    <a href='https://violetkester-warbler.onrender.com' target='_blank'>View Demo</a>
  </p>
</div>

<!-- content -->

<div>
  <h3>About</h3>
  <hr/>
  <p>
    <b>Developed with:</b><br/><br/>
    · Python<br/>
    · Flask<br/>
    · Jinja<br/>
    · PostgreSQL<br/>
    · SQLAlchemy<br/>
    · PostgreSQL<br/>
    · WTForms<br/>
    · Bootstrap<br/>
  </p>
  <h3>Log in</h3>
  <hr/>
  <p>
    <code>username: testuser</code><br />
    <code>password: password</code>
  </p>
  <h3>Running the application</h3>
  <hr/>
  <h4>1. Clone the repository.</h4>
  <p>
    <code>git clone https://github.com/violet-kester/warbler.git</code>
  </p>
    <h4>2. Set up a virtual environment.</h4>
  <p>
    <code>python3 -m venv venv</code><br/>
    <code>source venv/bin/activate</code>
  </p>
  <h4>
    3. Install dependencies.
  </h4>
  <p>
    <code>(venv) pip3 install -r requirements.txt</code>
  </p>
  <h4>
    4. Create and seed the database.
  </h4>
    <code>(venv) createdb warbler</code><br/>
    <code>(venv) python seed.py</code><br/>
  <p>
  </p>
  <h4>
    5. Create and configure environment variables in an `.env` file.
  </h4>
    <code>SECRET_KEY=abc123</code><br/>
    <code>DATABASE_URL=postgresql:///warbler</code><br/>
  <p>
  <h4>
    6. Start the server.
  </h4>
  <p>
    <code>(venv) flask run</code>
  <p>
  <p>
    Open the app in your browser at <a href='http://localhost:5000'>http://localhost:5000</a>.
  </p>
</div>

<!-- images  -->

<div align='center'>
  <h3>Images</h3>
  <hr/>
  <div class='images-container'>
    <img src='/static/images/warbler-screenshot-1.png' alt='Warbler screenshot 1'>
    <img src='/static/images/warbler-screenshot-2.png' alt='Warbler screenshot 2'>
    <img src='/static/images/warbler-screenshot-3.png' alt='Warbler screenshot 3'>
    <img src='/static/images/warbler-screenshot-4.png' alt='Warbler screenshot 4'>
  </div>
</div>