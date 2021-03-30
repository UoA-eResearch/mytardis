import React, {  useCallback, useState } from 'react'
import PropTypes from 'prop-types';
import { FiPieChart, FiLock, FiRefreshCcw } from 'react-icons/fi';
import Tooltip from 'react-bootstrap/Tooltip';
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Nav from 'react-bootstrap/Nav';
import { useSelector, useDispatch } from "react-redux";
import { 
    updateHighlightedResult,
    updateSelectedType,
    totalHitsSelector,
    pageSizeSelector,
    pageFirstItemIndexSelector,
    toggleItemSelected,
    getSelectedItems,
    selectPageItems,
    deselectAllItems,
    selectAllTypeItems,
    SELECTION_STATE
} from "./searchSlice";
import './ResultSection.css';
import EntryPreviewCard from './PreviewCard/EntryPreviewCard';
import Pager from "./sort-paginate/Pager";
import SortOptionsList from './sort-paginate/SortOptionsList';
import { typeSelector } from './filters/filterSlice';
import Button from "react-bootstrap/Button";
import { addItems } from "@apps/cart/cartSlice";
import { AiOutlineLoading } from 'react-icons/ai';
import { Alert, Spinner } from 'react-bootstrap';

export function PureResultTabs({ counts, selectedType, onChange }) {
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
                        <span className="text-capitalize">{name}</span> {hitTotal !== null &&
                            <span>
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

PureResultTabs.propTypes = {
    counts: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string.isRequired,
        id: PropTypes.string.isRequired,
        hitTotal: PropTypes.number
    })).isRequired,
    selectedType: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired
};

export const ResultTabs = () => {
    const selectedType = useSelector(state => state.search.selectedType);
    const dispatch = useDispatch();
    const onSelectType = useCallback(
        (type) => {
            dispatch(updateSelectedType(type));
        },
        [dispatch]);
    const hitTotalsByType = useSelector(state => {
        // Returns a list of object types, along with the number of hits they have.
        // If there aren't any results, then we return a null (which is different from a search being done with zero results)
        const hitTotals = state.search.results ? state.search.results.totalHits : null;
        return state.filters.types.allIds.map(
            typeId => {
                const typeCollectionName = typeSelector(state.filters, typeId).collection_name;
                return {
                    name: typeCollectionName,
                    id: typeId,
                    hitTotal: hitTotals ? hitTotals[typeId] : null
                };
            }
        );
    });
    return (<PureResultTabs counts={hitTotalsByType} selectedType={selectedType} onChange={onSelectType} />);
};




const NameColumn = {
    "project": "name",
    "experiment": "title",
    "dataset": "description",
    "datafile": "filename"
};

export function DownloadRightsIndicator({accessRights}) {
    if (accessRights === "none") {
        return <OverlayTrigger overlay={
            <Tooltip id="tooltip-no-download">
                You can&apos;t download this item.
            </Tooltip>
        }>
            <span><FiLock title="This item cannot be downloaded." /></span>
        </OverlayTrigger>;

    } else if (accessRights === "partial") {
        return <OverlayTrigger overlay={
            <Tooltip id="tooltip-partial-download">
                You can&apos;t download some files in this item.
            </Tooltip>
        //     <Popover id="blahasdfsdf">
        //     <PopoverTitle as="h3">Items added to download list.</PopoverTitle>
        //     <PopoverContent>
        //             Go to the Download tab to see what’s in your list and download them.
        //         <Button>OK, Got It.</Button>
        //     </PopoverContent>
        // </Popover>
        }>
            <span><FiPieChart title="Some files cannot be downloaded." /></span>
        </OverlayTrigger>;
    } else {
        return null;
    }
}

export function ResultRow({ result, onHighlight, isHighlighted, isSelected, onSelect }) {
    const type = result.type,
        resultName = result[NameColumn[type]],
        onKeyboardHighlight = (e) => {
            // Only respond to Enter key selects.
            if (e.key !== "Enter") {
                return;
            }
            onHighlight(result.id);
        };
    const handleItemSelected = useCallback((e) => {
        e.stopPropagation();
        e.nativeEvent.stopImmediatePropagation();
        onSelect(result.id);
    }, [onSelect, result.id]);
    return (
        <tr className={isHighlighted ? "result-section--row row-active-primary" : "result-section--row row-primary"} 
            onClick={onHighlight.bind(this, result.id)} 
            onKeyUp={onKeyboardHighlight} 
            tabIndex="0" 
            role="button">
            <td className="result-row--download-col">
                <input checked={isSelected} 
                    onChange={handleItemSelected}
                    className="download-col--selected" 
                    disabled={result.userDownloadRights === "none"} 
                    type="checkbox" 
                />
                <DownloadRightsIndicator accessRights={result.userDownloadRights} />
            </td>
            <td><a target="_blank" rel="noopener noreferrer" href={result.url}>{resultName}</a></td>
            <td>
                {result.userDownloadRights != "none" &&
                    <span>{result.size}</span>
                }
                {result.userDownloadRights === "none" &&
                    <span aria-label="Not applicable">&mdash;</span>
                }
            </td>
        </tr>
    );
}

ResultRow.propTypes = {
    result: PropTypes.object.isRequired,
    onHighlight: PropTypes.func.isRequired,
    isHighlighted: PropTypes.bool.isRequired,
    isSelected: PropTypes.bool.isRequired,
    onSelect: PropTypes.func.isRequired
};

export function PureResultList({ typeId }) {
    const dispatch = useDispatch();
    const isLoading = useSelector(state => state.search.isLoading);
    const error = useSelector(state => state.search.error);
    const results = useSelector(state => {
        const hitsByType = state.search.results ? state.search.results.hits : null;
        if (!hitsByType) {
            return [];
        }
        // Return the currently selected type of results as an array of items.
        return hitsByType[typeId].allIds.map(
            id => hitsByType[typeId].byId[id]
        );
    });
    const typeSelectedItems = useSelector(state => state.search.selected[typeId].items);
    const highlightedItem = useSelector(state => state.search.highlightedResult);
    const onItemHighlight = useCallback(highlightedResult => {
        if (isLoading) {
            // During loading, we disable selecting for preview card.
            return;
        }
        dispatch(updateHighlightedResult(highlightedResult));
    }, [dispatch, updateHighlightedResult]);
    const onToggleSelected = useCallback(id => {
        dispatch(toggleItemSelected({typeId, id: id}));
    }, [dispatch, typeId, toggleItemSelected]);
    let body, listClassName = "result-section__container";
    if (isLoading) {
        // Add the loading class to show effect.
        listClassName += " loading";
    }

    if (error) {
        return (
            // If there was an error during the search
            <div className="result-section--msg result-section--error-msg">
                <p>An error occurred. Please try another query, or reload the page and try searching again.</p>
                <p><Button onClick={() => location.assign("/search")}><FiRefreshCcw /> Reload</Button></p>
            </div>
        );
    }

    else if (!isLoading && results.length == 0) {
        // If the results are empty...
        body = (
            <tr>
                <td colSpan="3">
                    <div className="result-section--msg">
                        <p>No results. Please adjust your search and try again.</p>
                    </div>
                </td>
            </tr>
        );
    }

    else {
        // Render the results in table.
        body = results.map((result) => (
            <ResultRow key={result.id}
                onHighlight={onItemHighlight}
                result={result}
                isHighlighted={result.id === highlightedItem}
                isSelected={!!typeSelectedItems[result.id]}
                onSelect={onToggleSelected}
            />
        ));
    }

    return (
        <div className={listClassName}>
            <table className="table">
                <thead>
                    <tr>
                        <th>
                            <SelectAllCheckBox typeId={typeId} />
                        </th>
                        <th>Name</th>
                        <th>Size</th>
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
    typeId: PropTypes.number
};

const ResultSummary = ({typeId}) => {
    const currentCount = useSelector(state => totalHitsSelector(state.search, typeId));
    const currentPageSize = useSelector(state => pageSizeSelector(state.search, typeId));
    const currentFirstItem = useSelector(state => pageFirstItemIndexSelector(state.search, typeId));
    const currentLastItem = Math.min(currentCount, currentFirstItem + currentPageSize - 1);
    return (
        <p>
            <span>Showing {currentFirstItem} - {currentLastItem} of {currentCount} {currentCount > 1 ? "results" : "result"}.</span>
        </p>
    );
};

function SelectedItemToolbar({ typeId }) {
    const [isLoading, setIsLoading] = useState(false);
    const dispatch = useDispatch();
    const selectedItems = useSelector(state => getSelectedItems(state.search, typeId));
    const selectionState = useSelector(state => state.search.selected[typeId].selectionState);
    const numSelected = selectedItems.length;
    const handleSelectAll = useCallback(e => {
        e.preventDefault();
        setIsLoading(true);
        dispatch(selectAllTypeItems(typeId))
            // In any case, set loading state to false.
            .finally(() => setIsLoading(false));
    }, [dispatch, selectAllTypeItems, typeId]);
    const handleAddSelectedToCart = useCallback(() => {
        dispatch(addItems(selectedItems));
    }, [dispatch, selectedItems]);
    const handleCloseToolbar = useCallback(() => {
        dispatch(deselectAllItems({typeId}));
    }, [dispatch, typeId]);
    const itemWord = numSelected === 1 ? "item" : "items";
    const renderSummary = () => {
        switch (selectionState) {
            case SELECTION_STATE.All:
                return `All ${numSelected} result ${itemWord} selected.`;
            case SELECTION_STATE.Page:
                return `${numSelected} result ${itemWord} of this page selected.`;
            default:
                return `${numSelected} result ${itemWord} selected.`;
        }
    };

    if (isLoading) {
        return <Spinner animation="border" size="sm" role="status" />;
    }
    
    return (
        <Alert variant="secondary" onClose={handleCloseToolbar} dismissible>
            {renderSummary()}
            <Button className="ml-2" variant="primary" onClick={handleAddSelectedToCart}>Add to Cart</Button>
            {selectionState === SELECTION_STATE.Page &&
                <strong>
                    <Button variant="link" onClick={handleSelectAll}>Select all results</Button>
                </strong>
            }
        </Alert>);
}

SelectedItemToolbar.propTypes = {
    typeId: PropTypes.string.isRequired
};

function SelectAllCheckBox({ typeId }) {
    const selectionState = useSelector(state => state.search.selected[typeId].selectionState);
    const dispatch = useDispatch();
    const pageOrAllSelected = selectionState === SELECTION_STATE.All || selectionState === SELECTION_STATE.Page;
    const handleSelectButtonClicked = useCallback(() => {
        if (pageOrAllSelected) {
            dispatch(deselectAllItems({typeId}));
        } else {
            dispatch(selectPageItems({typeId}));
        }
    }, [dispatch, selectionState]);
    const isSelecting = selectionState === SELECTION_STATE.None || selectionState === SELECTION_STATE.Some;
    return (
            <>
            <label 
                className="sr-only" 
                htmlFor={"select-all-" + typeId}>
                {isSelecting ? "Select all results on this page" : "Deselect all results"}
            </label>
                <input 
                    id={"select-all-" + typeId} 
                    checked={pageOrAllSelected} 
                    onChange={handleSelectButtonClicked}
                    className="download-col--selected" 
                    type="checkbox" 
                />
            </>
    );
}

export function ResultItemToolbar({typeId}) {
    const numTypeSelectedItems = useSelector(
        state => Object.keys(
            state.search.selected[typeId].items
        ).length);
    return (
        <div className="tabpanel__toolbar">
            {numTypeSelectedItems > 0 ?
                <SelectedItemToolbar typeId={typeId} /> :
                <SortOptionsList typeId={typeId} />
            }
        </div>
    );
}

export function ResultTabPanes() {
    const selectedType = useSelector(state => state.search.selectedType);
    const types = useSelector(state => state.filters.types.allIds);
    const error = useSelector(state => state.search.error);
    // Create a tab pane to show each type's results.
    return types.map(typeId => (
        <div 
            key={typeId} 
            role="tabpanel" 
            className={"result-section--tabpanel " + ((typeId !== selectedType) ? "d-none" : "")} 
        >
            {!error && (
            <>
                <ResultSummary typeId={typeId} />
            </>
            )}
            <ResultItemToolbar typeId={typeId} />
            <div className="tabpanel__container--horizontal">
                <PureResultList 
                    typeId={typeId}
                />
                {!error &&
                <EntryPreviewCard />
                }
            </div>
            {!error &&
            <Pager objectType={typeId} />
            }
        </div>
    ));
}

export function PureResultSection({ selectedType, error }) {
    return (
        <section className="d-flex flex-column flex-grow-1 overflow-hidden">
            <ResultTabs />
            <ResultTabPanes />
        </section>
    );
}

export default function ResultSection() {
    const selectedType = useSelector(state => state.search.selectedType),
        error = useSelector(
            (state) => state.search.error
        );

    return (
        <PureResultSection
            error={error}
            selectedType={selectedType}
        />
    );
}
