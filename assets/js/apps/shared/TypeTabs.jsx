import React from "react";
import PropTypes from "prop-types";
import { Nav } from "react-bootstrap";
import { BsExclamationTriangleFill } from "react-icons/bs";
import "./TypeTabs.css";
/*
    This is a shared presentational component for displaying a set
    of tabs for each MyTardis object type.
    For example, it is used in the cart page for displaying a list
    of cart items, grouped by MyTardis object types.
*/
export function TypeTabs({ counts, selectedType, onChange }) {
    const handleNavClicked = (key) => {
        if (key !== selectedType) {
            onChange(key);
        }
    };

    return (
        <Nav variant="tabs" role="tablist" activeKey={selectedType}>
            {counts.map(({ id, name, hitTotal, hasWarning }) => (
                <Nav.Item role="tab" key={id}>
                    <Nav.Link onSelect={handleNavClicked.bind(this, id)} eventKey={id}>
                        {hasWarning ? <span className="type-tab--warning-icon"><BsExclamationTriangleFill title="This tab has problems." /></span> : null}
                        <span className="text-capitalize">{name}</span>
                        {(hitTotal !== undefined && hitTotal !== null) &&
                            <span>
                                {" "}
                                (
                                {hitTotal}
                                <span className="sr-only">
                                    {hitTotal > 1 ? " results" : " result"}
                                </span>
                                )
                            </span>
                        }
                    </Nav.Link>
                </Nav.Item>
            ))}
        </Nav>
    );
}

TypeTabs.propTypes = {
    counts: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string.isRequired,
        id: PropTypes.string.isRequired,
        hitTotal: PropTypes.number,
        hasWarning: PropTypes.bool
    })).isRequired,
    selectedType: PropTypes.string,
    onChange: PropTypes.func.isRequired
};
