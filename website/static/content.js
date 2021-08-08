import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

function PasswordManagerApp(props) {
  const [searchURL, setSearchURL] = useState('');
  const [message, setMessage] = useState('');
  const [data, setData] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [updatingData, setUpdatingData] = useState({});

  function search() {
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
    axios.post("/generate_new_react", {
      generate_new: data.id,
    }).then(res => {
      setData(res.data);
      setMessage(`Record ${data.id.toString()} updated successfully!`);
      copyPass();
    }).catch(error => {
      setData(null);
      if (error.response.status === 403) {
        setMessage(data.id.toString() + ' is invalid ID');
      } else if (error !== undefined) {
        setMessage(error.message);
      }
    });
  }

  function startUpdate () {
    setUpdating(true);
    setUpdatingData({...updatingData,
      ["login"]: data.login,
      ["remark"]: data.remark,
      ["password"]: data.password,
    });
  }

  function confirmUpdate () {
    axios.post("/update_db_react", {
      id: data.id,
      login: updatingData.login,
      remark: updatingData.remark,
      password: updatingData.password,
    }).then(res => {
      setData(res.data);
      setMessage(`Record ${data.id.toString()} updated sucessfully!`);
      setUpdatingData(false);
    }).catch(error => {
      setData(null);
      if (error.response.status === 403) {
        setMessage(data.id.toString() + ' is invalid ID');
      } else if (error !== undefined) {
        setMessage(error.message);
      }
    });
  }

  function delEntry () {
    console.log("deleting");
  }

  let editPane;
  if (data) {
    editPane = <div>
      <h2>URL: https://{data.url}</h2>
      {updating?
        <input
          type="password"
          placeholder="Enter new password"
          onChange={e => { setUpdatingData({...updatingData, ["password"]:e.target.value }) }}
        />
        : <div>
          <button onClick={copyPass}>Copy Password</button>
          <span> </span>
          <button onClick={genNewPass}>Generate Password</button>
        </div>
      }
      <table>
      <tbody>
        <tr>
          <th id="col-login">Login ID</th>
          <th id="col-remark">Notes</th>
          <th id="col-actions">Actions</th>
        </tr>
        <tr>
          <td>
            {updating?
              <input
                className="input-update"
                type="text"
                placeholder={data.login}
                defaultValue={data.login}
                onChange={e => { setUpdatingData({...updatingData, ["login"]:e.target.value }) }}
              /> : data.login
            }
          </td>
          <td>
            {updating?
              <input
                className="input-update"
                type="text"
                placeholder={data.remark}
                defaultValue={data.remark}
                onChange={e => { setUpdatingData({...updatingData, ["remark"]:e.target.value }) }}
              /> : data.remark
            }
          </td>
          <td>
            <button
              className="btn-sm"
              onClick={updating? confirmUpdate : startUpdate}
            >{updating? "Confirm" : "Update"}
            </button>
            {updating?
              <button
                className="btn-sm"
                onClick={() => setUpdating(false)}
              >Cancel</button> : null
            }<br/>
            <button
              className="btn-sm"
              onClick={delEntry}
              disabled={updating? true : false}
            >Delete</button>
          </td>
        </tr>
      </tbody>
      </table>
      {updatingData?
        <ul>
          <li>Note: Leave Password field blank if you don't want to update the password.</li>
          <li>Enter punctuations-only will generate a password with punctuations pick from them.</li>
          <li>Or you can enter a password directly.</li>
        </ul>
      : ""}
      <br/>
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
