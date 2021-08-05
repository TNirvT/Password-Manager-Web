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
      } else if (error !== undefined) {
        setMessage(error.message);
      }
    });
  }

  function copyPass () {
    navigator.clipboard.writeText(data.password);
  }

  function genNewPass () {
    console.log("updating " + data.id);
    axios.post("/generate_new_react", {
      generate_new: data.id,
    }).then(res => {
      setData(res.data);
      setMessage(`Record ${data.id.toString()} updated successfully!`);
    }).catch(error => {
      setData(null);
      if (error.response.status === 403) {
        setMessage(data.id.toString() + ' is invalid ID');
      } else if (error !== undefined) {
        setMessage(error.message);
      }
    });
  }

  function custPass () {
    console.log("custPass")
  }

  let editPane;
  if (data) {
    editPane = <div>
      <h2>URL: https://{data.url}</h2>
      <button onClick={copyPass} >Copy Password</button>
      <span> </span>
      <button onClick={genNewPass}>Generate Password</button>
      <span> </span>
      <button onClick={custPass}>Custom Password</button>
      <table>
      <tbody>
        <tr>
          <th>Login ID</th><th>Notes</th><th>Actions</th>
        </tr>
        <tr>
          <td id="col-login">{data.login}</td>
          <td id="col-remark">{data.remark}</td>
          <td id="col-actions">
            <button className="btn-sm">Update</button><br/>
            <button className="btn-sm">Delete</button>
          </td>
        </tr>
      </tbody>
      </table><br/>
      {/* Login: <input type="textbox" value={data.login} />
      Remarks: <input type="textbox" value={data.remark} /> */}
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
