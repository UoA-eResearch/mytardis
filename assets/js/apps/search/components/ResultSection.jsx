import React, { useState, useContext, useCallback } from 'react'
import Table from 'react-bootstrap/Table';
import PropTypes from 'prop-types';
import { FiPieChart, FiLock } from 'react-icons/fi';
import Tooltip from 'react-bootstrap/Tooltip';
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Nav from 'react-bootstrap/Nav';
import Badge from 'react-bootstrap/Badge';
import { useSelector, useDispatch } from "react-redux";
import { updateSelectedResult, updateSelectedType, totalHitsSelector, pageSizeSelector, pageFirstItemIndexSelector } from "./searchSlice";
import './ResultSection.css';
import EntryPreviewCard from './PreviewCard/EntryPreviewCard';
import Pager from "./sort-paginate/Pager";
import SortOptionsList from './sort-paginate/SortOptionsList';

export function PureResultTabs({ counts, selectedType, onChange }) {

    if (!counts) {
        counts = {
            experiments: null,
            datasets: null,
            datafiles: null,
            projects: null
        }
    }

    const handleNavClicked = (key) => {
        if (key !== selectedType) {
            onChange(key);
        }
    }

    const renderTab = (key, label) => {
        const typeCollectionName = key + "s";
        return (
            <Nav.Item role="tab">
                <Nav.Link onSelect={handleNavClicked.bind(this, key)} eventKey={key}>
                    {label} {counts[typeCollectionName] !== null &&
                        <span>
                        (
                            {counts[typeCollectionName]}
                            <span className="sr-only">{counts[typeCollectionName] > 1 ? " results" : " result"}</span>
                        )
                        </span>
                    }
                </Nav.Link>
            </Nav.Item>
        );
    }

    return (
        <Nav variant="tabs" activeKey={selectedType}>
            {renderTab("project", "Projects")}
            {renderTab("experiment", "Experiments")}
            {renderTab("dataset", "Datasets")}
            {renderTab("datafile", "Datafiles")}
        </Nav>
    )
}

PureResultTabs.propTypes = {
    counts: PropTypes.shape({
        projects: PropTypes.number,
        experiments: PropTypes.number,
        datasets: PropTypes.number,
        datafiles: PropTypes.number
    }),
    selectedType: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired
};

export const ResultTabs = () => {
    const hitTotals = useSelector(
        state => state.search.results ? state.search.results.totalHits : null
    );
    const selectedType = useSelector(state => state.search.selectedType);
    const dispatch = useDispatch();
    const onSelectType = useCallback(
        (type) => {
            dispatch(updateSelectedType(type));
        },
        [dispatch]);
    return (<PureResultTabs counts={hitTotals} selectedType={selectedType} onChange={onSelectType} />);
};




const NameColumn = {
    "project": "name",
    "experiment": "title",
    "dataset": "description",
    "datafile": "filename"
};

export function ResultRow({ result, onSelect, isSelected }) {
    const type = result.type,
        resultName = result[NameColumn[type]],
        onKeyboardSelect = (e) => {
            // Only respond to Enter key selects.
            if (e.key !== "Enter") {
                return;
            }
            onSelect(e);
        };
    return (
        <tr className={isSelected ? "result-section--row row-primary row-active-primary" : "result-section--row row-primary"} onClick={onSelect} onKeyUp={onKeyboardSelect} tabIndex="0" role="button">
            <td className="result-row--download-col">
                {result.userDownloadRights == "none" &&
                    <OverlayTrigger overlay={
                        <Tooltip id="tooltip-no-download">
                            You can't download this item.
                            </Tooltip>
                    }>
                        <span><FiLock title="This item cannot be downloaded." /></span>
                    </OverlayTrigger>
                }
                {result.userDownloadRights == "partial" &&
                    <OverlayTrigger overlay={
                        <Tooltip id="tooltip-partial-download">
                            You can't download some files in this item.
                            </Tooltip>
                    }>
                        <span><FiPieChart title="Some files cannot be downloaded." /></span>
                    </OverlayTrigger>
                }
            </td>
            <td><a target="_blank" href={result.url}>{resultName}</a></td>
            <td>
                {result.userDownloadRights != "none" &&
                    <span>{result.size}</span>
                }
                {result.userDownloadRights == "none" &&
                    <span aria-label="Not applicable">&mdash;</span>
                }
            </td>
        </tr>
    )
}

ResultRow.propTypes = {
    result: PropTypes.object.isRequired,
    onSelect: PropTypes.func.isRequired,
    isSelected: PropTypes.bool.isRequired
}

export function PureResultList({ results, selectedItem, onItemSelect, error, isLoading }) {
    results = results || [];
    let body, listClassName = "result-section__container";
    const handleItemSelected = (id) => {
        if (isLoading) {
            // During loading, we disable selecting for preview card.
            return;
        }
        onItemSelect(id);
    };

    if (isLoading) {
        // Add the loading class to show effect.
        listClassName += " loading";
    }

    if (error) {
        return (
            // If there was an error during the search
            <div className="result-section--msg result-section--error-msg">
                <p>An error occurred. Please try another query, or refresh the page and try searching again.</p>
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
        )
    }

    else {
        // Render the results in table.
        body = results.map((result) => (
            <ResultRow key={result.id}
                onSelect={handleItemSelected.bind(this, result.id)}
                result={result}
                isSelected={result.id === selectedItem}
            />
        ));
    }

    return (
        <Table className={listClassName} responsive hover>
            <thead>
                <tr>
                    <th></th>
                    <th>Name</th>
                    <th>Size</th>
                </tr>
            </thead>
            <tbody>
                {body}
            </tbody>
        </Table>
    )
}

PureResultList.propTypes = {
    results: PropTypes.arrayOf(Object),
    error: PropTypes.string,
    isLoading: PropTypes.bool,
    selectedItem: PropTypes.number,
    onItemSelect: PropTypes.func
}

const ResultSummary = ({typeId}) => {
    const currentCount = useSelector(state => totalHitsSelector(state.search, typeId));
    const currentPageSize = useSelector(state => pageSizeSelector(state.search, typeId));
    const currentFirstItem = useSelector(state => pageFirstItemIndexSelector(state.search, typeId));
    const currentLastItem = Math.min(currentCount, currentFirstItem + currentPageSize - 1);
    return (
        <p className="result-section--count-summary">
            <span>Showing {currentFirstItem} - {currentLastItem} of {currentCount} {currentCount > 1 ? "results" : "result"}.</span>
        </p>
    );
};

export function PureResultSection({ resultSets, selectedType,
    selectedResult, onSelectResult, isLoading, error }) {
    let selectedEntry = getSelectedEntry(resultSets, selectedResult, selectedType);
    const currentResultSet = resultSets ? resultSets[selectedType + "s"] : null;
    return (
        <>
            <ResultTabs />
            <div role="tabpanel" className="result-section--tabpanel">
                {!error &&
                    <>
                    <ResultSummary typeId={selectedType} />
                    <SortOptionsList typeId={selectedType} />
                    </>
                }
                <div className="tabpanel__container--horizontal">
                    <PureResultList results={currentResultSet} selectedItem={selectedResult} onItemSelect={onSelectResult} isLoading={isLoading} error={error} />
                    {!error &&
                        <EntryPreviewCard
                            data={selectedEntry}
                        />
                    }
                </div>
                {!error &&
                    <Pager objectType={selectedType} />
                }
            </div>
        </>
    )
}


/**
 * Returns the data of the selected row. Returns null if it cannot get find the selected result.
 * @param {*} resultSets 
 * @param {*} selectedResult 
 * @param {*} selectedType 
 */
function getSelectedEntry(resultSets, selectedResult, selectedType) {
    let selectedEntry = null;
    if (resultSets && selectedResult) {
        selectedEntry = resultSets[selectedType + "s"].filter(result => result.id === selectedResult)[0];
    }
    return selectedEntry;
}

export default function ResultSection() {
    const selectedType = useSelector(state => state.search.selectedType),
        selectedResult = useSelector(state => state.search.selectedResult),
        dispatch = useDispatch(),
        onSelectResult = (selectedResult) => {
            dispatch(updateSelectedResult(selectedResult));
        },
        resultSets = useSelector(
            (state) => state.search.results ? state.search.results.hits : null
        ),
        error = useSelector(
            (state) => state.search.error
        ),
        isLoading = useSelector(
            (state) => state.search.isLoading
        );

    return (
        <PureResultSection
            resultSets={resultSets}
            error={error}
            isLoading={isLoading}
            selectedType={selectedType}
            selectedResult={selectedResult}
            onSelectResult={onSelectResult}
        />
    )
}
