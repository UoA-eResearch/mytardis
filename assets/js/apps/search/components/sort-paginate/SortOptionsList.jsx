import React, { useCallback, useMemo } from "react";
import { DropdownButton, Dropdown, Form, Row } from "react-bootstrap";
import { typeAttrSelector, allTypeAttrIdsSelector } from "../filters/filterSlice";
import { SORT_ORDER, updateResultSort, removeResultSort, activeSortSelector, runSingleTypeSearch, sortableAttributesSelector, sortOrderSelector } from "../searchSlice";
import { useSelector, useDispatch } from "react-redux";
import PropTypes from "prop-types";
import { AiOutlineSortAscending, AiOutlineSortDescending } from "react-icons/ai";
import "./SortOptionsList.css";

const getSortSummaryText = (activeAttributes) => {
    if (activeAttributes.length === 0) {
        return "Sort";
    } else if (activeAttributes.length === 1) {
        return `Sort: ${activeAttributes[0].full_name}`;
    } else {
        return `Sort: ${activeAttributes[0].full_name} and ${activeAttributes.length - 1} more`;
    }
};
export function PureSortOptionsList({attributesToSort = [], activeSort, onSortUpdate, onSortRemove}) {
    if (!activeSort) {
        activeSort = [];
    }
    // Generate a hashmap of attributes and their sort options by ID.
    const attributeMap = useMemo(() => {
        const attrMap = {};
        attributesToSort.forEach(attribute => {
            const attributeSort = activeSort.filter(sortId => sortId === attribute.id);
            const hasActiveSort = attributeSort.length > 0;
            attrMap[attribute.id] = { attribute, hasActiveSort };
        });
        return attrMap;
    }, [attributesToSort, activeSort]);

    const activeAttributes = useMemo(() => (
        activeSort.map(sort => (attributeMap[sort].attribute))
    ), [activeSort, attributeMap]);

    const attributeHasActiveSort = useCallback(attributeId => {
        return attributeMap[attributeId].hasActiveSort;
    }, [attributeMap]);

    const handleActiveClicked = useCallback((attribute, e) => {
        if (e.target.checked) {
            // Update sort to activate it
            if (attributeHasActiveSort(attribute.id)) {
                // Sort is already active, do not continue.
                return;
            }
            onSortUpdate(attribute.id, attribute.order);
        } else {
            if (!attributeHasActiveSort(attribute.id)) {
                return;
            }
            onSortRemove(attribute.id);
        }
    }, [attributeHasActiveSort, onSortUpdate, onSortRemove]);
    const handleOrderClicked = useCallback((attribute, order, e) => {
        if (!e.target.checked) {
            return;
        } else {
            onSortUpdate(attribute.id, order);
        }
    }, [onSortUpdate]);
    const hasActiveSort = activeSort.length > 0;
    return (       
        <DropdownButton title={<>
                <AiOutlineSortAscending />
                <span>
                    { getSortSummaryText(activeAttributes) }
                </span>
            </>} variant={hasActiveSort ? "primary" : "outline-primary" } className="sortoptions">
            {
                attributesToSort.map(attribute => {
                    const { id, full_name, order } = attribute;
                    const isActive = attributeMap[id].hasActiveSort;
                    return (
                        <Dropdown.ItemText key={id} className="sortoptions--item">
                            <div className="sortoptions-item--check">
                                <Form.Check
                                    checked={isActive}
                                    onChange={handleActiveClicked.bind(this, attribute)}
                                    type="checkbox"
                                    id={id + "-sort-active"}
                                />
                            </div>
                            <div className="sortoptions-item--label">
                                <label htmlFor={id + "-sort-active"}>
                                    {full_name}
                                </label>
                            </div>
                            <div class="sortoptions-item--sortorder">
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
                            </div>
                        </Dropdown.ItemText>
                    ); 
                })
            }
        </DropdownButton>
    );
}

PureSortOptionsList.propTypes = {
    attributesToSort: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string.isRequired,
        full_name: PropTypes.string.isRequired,
        order: PropTypes.string
    })).isRequired,
    activeSort: PropTypes.arrayOf(PropTypes.string),
    onSortUpdate: PropTypes.func.isRequired,
    onSortRemove: PropTypes.func.isRequired
};

export default function SortOptionsList({typeId}) {

    const dispatch = useDispatch();
    const allSortOptions = useSelector(state => {
        // Grab all type attributes, except for schema - not applicable in this case.
        const sortableAttributes = sortableAttributesSelector(state.filters, typeId);
        return sortableAttributes.map(({id, full_name}) => {
            const order = sortOrderSelector(state.search, typeId);
            return {
                id,
                full_name,
                order
            };
        });
    });
    const activeSort = useSelector(state => activeSortSelector(state.search, typeId));

    const handleSortUpdate = useCallback((attributeId, order) => {
        dispatch(updateResultSort({
            typeId,
            attributeId,
            order
        }));
        dispatch(runSingleTypeSearch(typeId));
    }, [dispatch, typeId]);

    const handleSortRemove = useCallback(attributeId => {
        dispatch(removeResultSort({
            typeId,
            attributeId
        }));
        dispatch(runSingleTypeSearch(typeId));
    }, [dispatch, typeId]);

    return (
        <PureSortOptionsList 
            activeSort={activeSort}
            attributesToSort={allSortOptions}
            onSortRemove={handleSortRemove}
            onSortUpdate={handleSortUpdate}
        />
    );
}
