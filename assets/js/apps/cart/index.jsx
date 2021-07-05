import React, { useCallback } from "react";
import ReactDOM from "react-dom";
import "./cart.css";
import { Provider } from "react-redux";
import { HashRouter, Route, Switch } from "react-router-dom";
import store from "@apps/shared/reduxAppStore";
import "bootstrap/dist/css/bootstrap.css";
import TransferScreen from "./TransferScreen";
import CartScreen from "./CartScreen";



ReactDOM.render(
    <HashRouter>
        <Provider store={store}>
            <div className="container">
                <main className="cart-content shadow-sm">
                    <Switch>
                        <Route path="/transfer">
                            <TransferScreen />
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