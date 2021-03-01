import React, { Component, useState, useEffect } from "react";
import "./ProjectPage.css";
import ExperimentList from "../ExperimentList/ExperimentList";
import { Alert, Spinner } from "react-bootstrap";

export default function ProjectPage(props) {

  let projectName = props.name;
  let projectDescription = props.description;
  return (
    <div className="project">
      <h2 className="project__label">Project</h2>
      <h1 className="project__name">{projectName}</h1>
      <div className="project__description">{projectDescription}</div>
      <ExperimentList experiments={props.experiments} />
    </div>
  );
}
