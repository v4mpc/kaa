chrome.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
        if (request.message === "clicked_browser_action") {


            console.log("browser action clicked!!");
        }
    }
);

// console.log('url matches send request to server')