import PropTypes from "prop-types";
import React from "react";
import Button from "react-bootstrap/Button";
import { FiRefreshCcw } from "react-icons/fi";

export function PureResultList({ children, headers, error, isLoading }) {
    let body, listClassName = "result-section__container";

    if (isLoading) {
        // Add the loading class to show effect.
        listClassName += " loading";
    }

    if (error) {
        return (
            // If there was an error during the search
            <div className="result-section--msg result-section--error-msg">
                <p>An error occurred. Please reload the page and try again.</p>
                <p><Button onClick={() => location.assign("/apps/cart")}><FiRefreshCcw /> Reload</Button></p>
            </div>
        );
    }

    else if (!isLoading && !children) {
        // If the results are empty...
        body = (
            <tr>
                <td colSpan="3">
                    <div className="result-section--msg">
                        <p>Your cart is empty.</p>
                    </div>
                </td>
            </tr>
        );
    } else {
        body = children;
    }

    return (
        <div className={listClassName}> 
            <table className="table">
                <thead>
                    <tr>
                        {headers.map((header,idx) => <th key={header + idx}>{header}</th>)}
                    </tr>
                </thead>
                <tbody>
                    {body}
                </tbody>
            </table>
        </div>
    )
}

PureResultList.propTypes = {
    results: PropTypes.arrayOf(Object),
    error: PropTypes.string,
    isLoading: PropTypes.bool,
    children: PropTypes.node,
    headers: PropTypes.arrayOf(PropTypes.string.isRequired)
};


export function PureCartRow({typeId, data}) {

}

PureCartRow.propTypes = {
    data: PropTypes.shape({
        size: PropTypes.number.isRequired,
        
    })
}