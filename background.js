// Called when the user clicks on the browser action.
chrome.browserAction.onClicked.addListener(function (tab) {
    // Send a message to the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        var activeTab = tabs[0];
        chrome.tabs.sendMessage(activeTab.id, { "message": "clicked_browser_action" });
    });
});

chrome.webNavigation.onBeforeNavigate.addListener(sendRequest, {
    url: [
        { urlPrefix: 'https://www.beforward.jp', pathContains: 'id' },

    ]
});

function sendRequest(e) {
    let data_url = e.url
    let url = new URL('http://127.0.0.1:8000/valuate')
    url.search = new URLSearchParams({
        url: data_url,
    })
    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
    }).then(response => {

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json()
    }).then(data => {
        console.log(data)
        console.log(data_url)

        let store_object = {}
        store_object[data_url] = data
        chrome.storage.sync.set(store_object, function () {



            chrome.runtime.sendMessage({ "message": "data_ready" })




        });



    })

}