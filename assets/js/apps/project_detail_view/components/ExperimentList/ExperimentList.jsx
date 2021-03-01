import React, { useState, useEffect } from "react";
import "./ExperimentList.css";
import { Alert, Spinner } from "react-bootstrap";

export default function ExperimentList(experiments) {

  const exps = experiments.experiments;

  if (exps.length == 0) {
    return (
      <Alert variant="primary">
        No experiments found for this project.
      </Alert>
    )
  }
  return (
    <div className="table__container">
      <h3 className="table__header">Experiments in this project</h3>
      <table className="experiment__table">
        <tbody>
          {Object.keys(exps).map((expkey, i) => {
            let experimentLink = `/experiment/view/${exps[expkey].id}`;
            return (
              <tr key={i}>
                <td>
                  <a className="experiment__link" href={experimentLink}>
                    {exps[expkey].title}
                  </a>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  );
};
