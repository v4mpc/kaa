var myApp = angular.module("my-app", []);

myApp.controller("PopupCtrl", function ($scope, $http, $timeout) {



    console.log("Controller Initialized");


    $scope.showSpinner = true;


    chrome.tabs.query({ active: true, lastFocusedWindow: true }, tabs => {
        let url = tabs[0].url;

        chrome.storage.sync.get([url], function (result) {
            if (result) {

                console.log('got data locally')
                setScopeResult(result[url])
                sendRequest(url)
            } else {
                console.log("added event listener")
                chrome.runtime.onMessage.addListener(
                    function (request, sender, sendResponse) {
                        if (request.message === "data_ready") {
                            console.log('data_ready')
                            chrome.storage.sync.get([url], function (result) {
                                setScopeResult(result[url])


                            })
                        }
                    }
                );


            }
        });




    });








    function sendRequest(url) {

        $http({
            url: 'http://127.0.0.1:8000/valuate',
            method: "get",
            params: {
                url: url
            }
        })
            .then(function (response) {
                // success
                $scope.showSpinner = false
                console.log("success in getting reponse from backend API");
                console.log("response: " + JSON.stringify(response));
                $scope.result = {
                    model: response.data.model,
                    make: response.data.make,
                    bodytype: response.data.bodytype,
                    yearofmanufacture: response.data.yearofmanufacture,
                    country: response.data.country,
                    fueltype: response.data.fueltype,
                    rengine: response.data.rengine,
                    price: response.data.price,
                    totalimporttaxes: response.data.totalimporttaxes,
                    vehicleregistrationfee: response.data.vehicleregistrationfee,
                    totaltaxes: response.data.totalimporttaxes,
                    grandtotal: response.data.grandtotal,
                }
                console.log($scope.result)
            },
                function (response) { // optional
                    // failed
                    console.log(response)
                    $scope.showSpinner = false
                    console.log("failure in getting response from backend API");
                });
    }


    function setScopeResult(data) {

        $scope.result = {
            model: data.model,
            make: data.make,
            bodytype: data.bodytype,
            yearofmanufacture: data.yearofmanufacture,
            country: data.country,
            fueltype: data.fueltype,
            rengine: data.rengine,
            price: data.price,
            totalimporttaxes: data.totalimporttaxes,
            vehicleregistrationfee: data.vehicleregistrationfee,
            totaltaxes: data.totalimporttaxes,
            grandtotal: data.grandtotal,
        }
        $scope.showSpinner = false
    }


    // Get Background Page to get selectedText from it's scope
    //    let bgPage = chrome.extension.getBackgroundPage();
    //    let selectedText = bgPage.selectedText;
    //    $scope.selectedText = selectedText;
    //    console.log("selectedText: " + selectedText);

    //    if(selectedText.length > 0) {
    //      $http({
    //           url: 'http://127.0.0.1:8000/valuate',
    //           method: "POST",
    //           data: {
    //             "encodingType": "UTF8",
    //             "document": {
    //               "type": "PLAIN_TEXT",
    //               "content": selectedText
    //             }
    //           }
    //       })
    //       .then(function(response) {
    //         // success
    //         console.log("success in getting reponse from backend API");
    //         console.log("response: " + JSON.stringify(response));

    //       },
    //       function(response) { // optional
    //         // failed
    //         console.log("failure in getting response from backend API");
    //       });
    //    }

}
);