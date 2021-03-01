import React, { Suspense, Fragment } from "react";
import ReactDOM from "react-dom";
import "./index.css";
import ProjectPage from "./components/ProjectPage/ProjectPage";
import * as serviceWorker from "./serviceWorker";


let mountPoint = document.getElementById('project-app');

const { href } = window.location;
// console.log(href);

const projectId = href.substring(href.lastIndexOf("/", href.lastIndexOf("/") - 1 ) + 1, href.lastIndexOf("/"));

ReactDOM.render(
    React.createElement(ProjectPage, window.props),    // gets the props that are passed in the template
    window.react_mount,                                // a reference to the #react div that we render to
)
// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
