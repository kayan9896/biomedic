import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorInfo: null };
    this.err = ''
  }
  
  componentDidCatch(error, errorInfo) {
    this.setState({ hasError: true, errorInfo });

    const errorMsg = `${error.toString()} at ${errorInfo.componentStack}`;
    this.err = errorMsg
    console.log(errorMsg, window.electronAPI); // Send to main process
    window.electronAPI?.logError(errorMsg);
  }

  render() {
    if (this.state.hasError) {
      return (
      <>
        <h2 style={{color:'white'}}>Something went wrong.</h2>
        <div style={{color:'white'}}>{this.err}</div>
        <img className="image-button" src={require('./L17/ShutDownBtn.png')} alt="ShutDownBtn" style={{position:'absolute', top:'539px', left:'1013px', zIndex:17}} onClick={() => {window.close()}}/>
      </>
      )
    }
    return this.props.children;
  }
}

export default ErrorBoundary;