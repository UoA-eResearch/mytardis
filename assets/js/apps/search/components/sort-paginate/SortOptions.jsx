import React from "react";
import { DropdownButton, Dropdown, Form, Row } from "react-bootstrap";
import { typeAttrSelector, allTypeAttrIdsSelector } from "../filters/filterSlice";
import { SORT_ORDER } from "../searchSlice";
import { useSelector } from "react-redux";
import PropTypes from "prop-types";
import { AiOutlineSortAscending, AiOutlineSortDescending } from "react-icons/ai";
import "./SortOptions.css";

const getSortSummaryText = (attributes) => {
    const activeAttributes = attributes.filter(attribute => attribute.isActive);
    if (activeAttributes.length === 0) {
        return "Sort";
    } else if (activeAttributes.length === 1) {
        return `Sort: ${activeAttributes[0].full_name}`;
    } else {
        return `Sort: ${activeAttributes[0].full_name} and ${activeAttributes.length - 1} more`; 
    }
};

export function PureSortOptions({attributesToSort}) {
    return (       
        <DropdownButton title={getSortSummaryText(attributesToSort)} variant="outline-primary" className="sortoptions">
            {
                attributesToSort.map(attribute => {
                    const { id, full_name, isActive, order } = attribute;
                    return (
                        <Dropdown.ItemText key={id} className="sortoptions--item">
                            <Form.Group as={Row}>
                                <Form.Check checked={isActive} type="checkbox" id={id + "-sort-active"} />
                                <label htmlFor={id + "-sort-active"}>
                                    {full_name}
                                </label>
                                <Form.Check checked={order === SORT_ORDER.ascending} type="radio" name={id + "-sort-order"} id={id + "-sort-asc"} />
                                <label htmlFor={id + "-sort-asc"}>
                                    <AiOutlineSortAscending /><span className="sr-only">Sort ascending</span>
                                </label>
                                <Form.Check checked={order === SORT_ORDER.descending} type="radio" name={id + "-sort-order"} id={id + "-sort-desc"} />
                                <label htmlFor={id + "-sort-desc"}>
                                    <AiOutlineSortDescending /><span className="sr-only">Sort descending</span>
                                </label>
                            </Form.Group>
                        </Dropdown.ItemText>
                    ); 
                })
            }
        </DropdownButton>
    );
}

PureSortOptions.propTypes = {
    attributesToSort: PropTypes.arrayOf({
        id: PropTypes.string.isRequired,
        full_name: PropTypes.string.isRequired,
        order: PropTypes.string,
        isActive: PropTypes.bool.isRequired
    }).isRequired,
    onSortUpdated: PropTypes.func.isRequired,
    onSortRemoved: PropTypes.func.isRequired
};

export default function SortOptions({type}) {

    const allTypeAttributes = useSelector(state => {
        // Grab all type attributes, except for schema - not applicable in this case.
        const attributeIds = allTypeAttrIdsSelector(state.filters, type).filter(id => id !== "schema");
        return attributeIds.map(id => (
            typeAttrSelector(state.filters, type, id)
        ));
    });

    return (
        <div>
        </div>
    );
}
