history.pushState(null, document.title, location.href);
window.addEventListener('popstate', function (event) {
    history.pushState(null, document.title, location.href);
});

window.addEventListener('beforeunload', (event) => {
    event.preventDefault();
    // Chrome requires returnValue to be set.
    event.returnValue = '';
    return false;
});
// document.onkeydown = function(event){
//   switch (event.keyCode){
//         case 116 : //F5 button
//             event.returnValue = false;
//             event.keyCode = 0;
//             return false;
//         case 82 : //R button
//             if (event.ctrlKey){
//                 event.returnValue = false;
//                 event.keyCode = 0;
//                 return false;
//             }
//     }
// };
