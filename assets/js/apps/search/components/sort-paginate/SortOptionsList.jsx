import React, {useCallback} from "react";
import { DropdownButton, Dropdown, Form, Row } from "react-bootstrap";
import { typeAttrSelector, allTypeAttrIdsSelector } from "../filters/filterSlice";
import { SORT_ORDER, updateResultSort, removeResultSort, activeSortSelector } from "../searchSlice";
import { useSelector, useDispatch } from "react-redux";
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

export function PureSortOptionsList({attributesToSort, onSortUpdate, onSortRemove}) {
    const handleActiveClicked = useCallback((attribute, e) => {
        if (e.target.checked) {
            // Update sort to activate it
            if (attribute.isActive) {
                // Sort is already active, do not continue.
                return;
            }
            onSortUpdate(attribute.id, attribute.order);
        } else {
            if (!attribute.isActive) {
                return;
            }
            onSortRemove(attribute.id);
        }
    }, [onSortUpdate, onSortRemove]);
    const handleOrderClicked = useCallback((attribute, order, e) => {
        if (!e.target.checked) {
            return;
        } else {
            onSortUpdate(attribute.id, order);
        }
    }, [onSortUpdate]);
    return (       
        <DropdownButton title={getSortSummaryText(attributesToSort)} variant="outline-primary" className="sortoptions">
            {
                attributesToSort.map(attribute => {
                    const { id, full_name, isActive, order } = attribute;
                    return (
                        <Dropdown.ItemText key={id} className="sortoptions--item">
                            <Form.Group as={Row}>
                                <Form.Check
                                    checked={isActive}
                                    onChange={handleActiveClicked.bind(this, attribute)}
                                    type="checkbox"
                                    id={id + "-sort-active"}
                                />
                                <label htmlFor={id + "-sort-active"}>
                                    {full_name}
                                </label>
                                <Form.Check 
                                    checked={order === SORT_ORDER.ascending}
                                    onChange={handleOrderClicked.bind(this, attribute, SORT_ORDER.ascending)}
                                    type="radio"
                                    name={id + "-sort-order"}
                                    id={id + "-sort-asc"}
                                />
                                <label htmlFor={id + "-sort-asc"}>
                                    <AiOutlineSortAscending /><span className="sr-only">Sort ascending</span>
                                </label>
                                <Form.Check
                                    checked={order === SORT_ORDER.descending}
                                    onChange={handleOrderClicked.bind(this, attribute, SORT_ORDER.descending)}
                                    type="radio"
                                    name={id + "-sort-order"}
                                    id={id + "-sort-desc"}
                                />
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

PureSortOptionsList.propTypes = {
    attributesToSort: PropTypes.arrayOf({
        id: PropTypes.string.isRequired,
        full_name: PropTypes.string.isRequired,
        order: PropTypes.string,
        isActive: PropTypes.bool.isRequired
    }).isRequired,
    onSortUpdate: PropTypes.func.isRequired,
    onSortRemove: PropTypes.func.isRequired
};

export default function SortOptionsList({typeId}) {

    const dispatch = useDispatch();
    const allSortOptions = useSelector(state => {
        const activeSort = activeSortSelector(state.search, typeId);
        // Grab all type attributes, except for schema - not applicable in this case.
        const attributeIds = allTypeAttrIdsSelector(state.filters, typeId + "s").filter(id => id !== "schema");
        return attributeIds.map(id => {
            const { full_name } = typeAttrSelector(state.filters, typeId + "s", id);
            const sortOption = activeSort.filter(sort => sort.id === id);
            let order = SORT_ORDER.descending, isActive = false;
            if (sortOption.length > 0) {
                order = sortOption[0].order;
                isActive = true;
            }
            return {
                id,
                full_name,
                order,
                isActive
            };
        });
    });

    const handleSortUpdate = useCallback((attributeId, order) => {
        dispatch(updateResultSort({
            typeId,
            attributeId,
            order
        }));
    }, [dispatch, typeId]);

    const handleSortRemove = useCallback(attributeId => {
        dispatch(removeResultSort({
            typeId,
            attributeId
        }));
    }, [dispatch, typeId]);

    return (
        <PureSortOptionsList 
            attributesToSort={allSortOptions}
            onSortRemove={handleSortRemove}
            onSortUpdate={handleSortUpdate}
        />
    );
}
