import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

function PasswordManagerApp(props) {
  const [searchURL, setSearchURL] = useState('');
  const [message, setMessage] = useState('');
  const [data, setData] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [updatingData, setUpdatingData] = useState({});
  const [deleting, setDeleting] = useState(false);
  const minPwLength = 10;

  function search() {
    axios.get('/search_react', {
      params: {
        url_read: searchURL,
      },
    }).then(res => {
      setData(res.data);
      if (res.data.id === null) {
        setUpdating(true);
        setUpdatingData({...updatingData,
          ["login"]: "",
          ["remark"]: "",
          ["password"]: "",
        });
        setMessage("New URL detected. Add a new entry?")
      } else {
        setUpdating(false);
        setMessage("")
      };
    }).catch(error => {
      setData(null);
      if (error !== undefined) {
        setMessage(error.message);
      }
    });
  }

  function addNewEntry() {
    console.log("add new entry");
    axios.post("/insert_db_react",{
      url: data.url,
      login: updatingData.login,
      remark: updatingData.remark,
      password: updatingData.password,
    }).then(res => {
      setData(res.data);
      setMessage("New entry created!");
      setUpdating(false);
    }).catch(error => {
      setData(null);
      if (error !== undefined) {
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
      ["password"]: "",
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
      setUpdating(false);
    }).catch(error => {
      setData(null);
      if (error.response.status === 403) {
        setMessage(data.id.toString() + ' is invalid ID');
      } else if (error !== undefined) {
        setMessage(error.message);
      }
    })
  }

  function startDelete () {
    setDeleting(true);
  }

  function confirmDelete () {
    axios.post("/delete_react", {
      id: data.id,
    }).then(_ => {
      setData(null);
      setMessage(`Record ${data.id.toString()} deleted sucessfully!`);
      setDeleting(false);
    }).catch(error => {
      setData(null);
      if (error.response.status === 403) {
        setMessage(data.id.toString() + ' is invalid ID');
      } else if (error !== undefined) {
        setMessage(error.message);
      }
    })
  }

  let editPane;
  if (data) {
    editPane = <div>
      <h2>URL: https://{data.url}</h2>
      {updating?
        <input
          className="input-pw-ch"
          type="password"
          placeholder="Enter a new password"
          onChange={e => { setUpdatingData({...updatingData, ["password"]:e.target.value }) }}
        />
        : <div>
          <button onClick={copyPass} disabled={deleting? true : false}>Copy Password</button>
          <span> </span>
          <button onClick={genNewPass} disabled={deleting? true : false}>Generate Password</button>
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
                placeholder={data.id? data.login : "Enter your login id"}
                defaultValue={data.id && data.login}
                onChange={e => { setUpdatingData({...updatingData, ["login"]:e.target.value }) }}
              /> : data.login
            }
          </td>
          <td>
            {updating?
              <input
                className="input-update"
                type="text"
                placeholder={data.id? data.remark : "Additional note"}
                defaultValue={data.id && data.remark}
                onChange={e => { setUpdatingData({...updatingData, ["remark"]:e.target.value }) }}
              /> : data.remark
            }
          </td>
          <td>
            <button
              className="btn-sm"
              onClick={data.id ? (!updating ? startUpdate : confirmUpdate) : addNewEntry}
              disabled={deleting? true : false}
            >{updating? "Confirm" : "Update"}
            </button>
            {updating &&
              <button
                className="btn-sm"
                onClick={() => setUpdating(false)}
              >Cancel</button>
            }<br/>
            <button
              className="btn-sm btn-warn"
              onClick={deleting? confirmDelete : startDelete}
              disabled={updating? true : false}
            >{deleting? "Confirm" : "Delete"}
            </button>
            {deleting && 
              <button
                className="btn-sm"
                onClick={() => setDeleting(false)}
              >Cancel</button>
            }
          </td>
        </tr>
      </tbody>
      </table>
      {updating &&
        <ul className="list-notes">
          <li>Note: Leave Password field blank {data.id?
            "if you don't want to update the password."
          : "to generate a password by default parameters."
          }</li>
          <li>Enter punctuations-only will generate a password with punctuations pick from them.</li>
          <li>Or you can enter a password directly.</li>
          <li>Password should be at least <span color="red">{minPwLength}</span> characters.</li>
        </ul>
      }
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
