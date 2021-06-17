import React from "react";
import PropTypes from "prop-types";
import { Nav } from "react-bootstrap";


export function CategoryTabs({ counts, selectedType, onChange }) {
    const handleNavClicked = (key) => {
        if (key !== selectedType) {
            onChange(key);
        }
    };

    return (
        <Nav variant="tabs" role="tablist" activeKey={selectedType}>
            {counts.map(({ id, name, hitTotal }) => (
                <Nav.Item role="tab" key={id}>
                    <Nav.Link onSelect={handleNavClicked.bind(this, id)} eventKey={id}>
                        <span className="text-capitalize">{name}</span> 
                        {(hitTotal !== undefined && hitTotal !== null) &&
                            <span>{" "}
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

CategoryTabs.propTypes = {
    counts: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string.isRequired,
        id: PropTypes.string.isRequired,
        hitTotal: PropTypes.number
    })).isRequired,
    selectedType: PropTypes.string,
    onChange: PropTypes.func.isRequired
};
