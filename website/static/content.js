import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

function PasswordManagerApp(props) {
  const [searchURL, setSearchURL] = useState('');
  const [message, setMessage] = useState('');
  const [data, setData] = useState(null);

  function search() {
    console.log('Searching for ', searchURL);
    axios.get('/search_react', {
      params: {
        url_read: searchURL,
      },
    }).then(res => {
      setData(res.data);
    }).catch(error => {
      setData(null);
      if (error.response.status === 404) {
        setMessage(searchURL + ' is not found');
      } else {
        setMessage(error.message);
      }
    });
  }

  let editPane; 
  if (data) {
    editPane = <div>
      Login: <input type="textbox" value={data.login} />
      Remarks: <input type="textbox" value={data.remark} />
    </div>;
  }

  return (
    <React.Fragment>
      <div>
        <h1 className="heading">Password Vault React</h1>
        <div>
          <label>
            Search
            <input
              type="text"
              className="form-control"
              placeholder="Search URL"
              onChange={e => setSearchURL(e.target.value)}
            />
          </label>
        </div>
        <button
          className="btn-submit"
          onClick={search}>Submit</button>
      </div>
      <div>
        {message}
        {editPane}
      </div>
    </React.Fragment>
  );
}

ReactDOM.render(
    <PasswordManagerApp />,
    document.getElementById('react')
);
