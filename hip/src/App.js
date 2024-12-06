import HipOperationSoftware from './HipOperationSoftware';
function closewin(){
  const remote=(window.require)?window.require('electron').remote:null;
  const w=remote.getCurrentWindow()
  w.close()
}
function App() {
  
  return (
    <div className="App">
      <HipOperationSoftware />
      <button onClick={closewin}>close</button>
    </div>
  );
}

export default App;
