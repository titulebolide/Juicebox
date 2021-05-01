import React from 'react';


var API_URL = window.location.origin
if (process.env.NODE_ENV === 'development') {
  API_URL = 'http://localhost:8000'
}


class App extends React.Component {


  state = {
    volume : 0,
    title : "",
    playing : false,
    radioId : -1,
    radios: []
  }


  componentDidMount = () => {
    console.log(process.env)
    this.fetchInfos()
    fetch(API_URL + '/radios/').then( response => {
      response.json().then( data => {
        console.log(data)
        this.setState({
          radios: data.radios
        })
      })
    })
  }


  getCallAPI = (endpoint) => (
    e => fetch(API_URL + '/' + endpoint+'/').then(response => {
      this.fetchInfos()
    })
  )

  fetchInfos = () => (
    fetch(API_URL + '/state').then( response => {
      response.json().then( data => {
        this.setState({
          volume: data.volume,
          title: data.title,
          playing: data.playing,
          radioId: data.radioId
        })
      })
    })
  )


  getStyleRadioBtn = (id) => {
    if (id === this.state.radioId) return {'width':'100%', 'marginTop':'10px', 'color':'red', 'fontWeight':'bold'}
    else return {'width':'100%', 'marginTop':'10px'}
  }



  render = () => {
    if (this.state.title === "") return (
      <div style={{'display':'table','margin': '0 auto'}}>
         <div className="spinner-grow"  style={{'width': '3rem', 'height': '3rem'}} role="status">
           <span className="sr-only">Loading...</span>
         </div>
      </div>
    ); else return (
      <center style={{"width":"100vw"}}>
        <div style={{"width":"50%","minWidth":"350px"}}>

          <div style={{"borderBottom": "1px solid black", "margin": "10px", "padding": "10px"}}>
              <h2>
                  {this.state.title}
              </h2>
          </div>


          <div style={{'display':'flex'}}>
              <div style={{"flex":"1"}}>
                  <center>
                      <button
                          className = "btn btn-outline-secondary"
                          style = {{"width":"100%","marginTop":"10px","fontWeight":"bold"}}
                          onClick={this.getCallAPI("volumedown")}>
                          -
                      </button>
                  </center>
              </div>
              <div style={{"paddingTop":"18px","flex":"3"}}>
                  <center>
                      Volume : {this.state.volume} %
                  </center>
              </div>
              <div style={{"flex":"1"}}>
                  <center>
                      <button
                          className = "btn btn-outline-secondary"
                          style = {{"width":"100%","marginTop":"10px","fontWeight":"bold"}}
                          onClick={this.getCallAPI('volumeup')}>
                          +
                      </button>
                  </center>
              </div>
          </div>


          <div>
            <button
                className = "btn btn-outline-danger"
                style = {{"width":"100%","marginTop":"10px"}}
                onClick={this.getCallAPI('stop')}>
                Pause
            </button>
          </div>


          <div style={{'marginTop':'20px','marginBottom':'10px'}}>
              <iframe title="dummyframe" name="dummyframe" id="dummyframe" style={{"display": "none"}}/>
              <form action={API_URL + '/yt'} target="dummyframe" style={{"margin":"0"}}>
                  <div style={{'display':'flex'}}>
                      <input style={{'flex':'4', 'marginRight':'20px'}} type="text" id="url" name="url" placeholder='Youtube Video URL'/>
                      <button className="btn btn-outline-primary" style={{'flex':'1'}} type='submit'>Play</button>
                  </div>
              </form>
          </div>


          {this.state.radios && this.state.radios.length !== 0 && this.state.radios.map((radio,id) => (
            <div key={id}>
              <button
                className = "btn btn-outline-secondary"
                style = {this.getStyleRadioBtn(id)}
                onClick = {this.getCallAPI("radio/"+id)}>
              {radio.name}
              </button>
            </div>
          ))}

        </div>
      </center>
    )
  }
}

export default App;
