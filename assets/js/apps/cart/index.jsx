import React, { useCallback } from "react";
import ReactDOM from "react-dom";
import "./cart.css";
import { Provider } from "react-redux";
import { HashRouter, Route, Switch } from "react-router-dom";
import store from "@apps/shared/reduxAppStore";
import "bootstrap/dist/css/bootstrap.css";
import TransferScreen from "./TransferScreen";
import CartScreen from "./CartScreen";
import DownloadScreen from "./DownloadScreen";



ReactDOM.render(
    <HashRouter>
        <Provider store={store}>
            <div className="container">
                <main className="cart-content shadow-sm mt-4">
                    <Switch>
                        <Route path="/transfer">
                            <TransferScreen />
                        </Route>
                        <Route path="/download">
                            <DownloadScreen />
                        </Route>
                        <Route path="/">
                            <CartScreen />
                        </Route>
                    </Switch>
                </main>
            </div>      
        </Provider>
    </HashRouter>,
    document.getElementById("cart-app"),
);