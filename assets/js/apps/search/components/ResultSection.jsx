import React, { useState, useContext } from 'react'
import Table from 'react-bootstrap/Table';
import PropTypes from 'prop-types';
import { FiPieChart, FiLock } from 'react-icons/fi';
import Nav from 'react-bootstrap/Nav';
import Badge from 'react-bootstrap/Badge';
import SearchInfoContext from './SearchInfoContext';

export function ResultTabs({counts, selectedLevel, onChange}) {

    if (!counts) {
        counts = {
            experiment: null,
            dataset: null,
            datafile: null,
            project: null
        }
    }

    const handleNavClicked = (key) => {
        if (key !== selectedLevel){
            onChange(key);
        }
    }

    const renderTab = (key,label) => {
        // const badgeVariant = selectedLevel === key ? "primary":"secondary";
        const badgeVariant = "secondary";
        return (
        <Nav.Item role="tab">
            <Nav.Link onSelect={handleNavClicked.bind(this,key)} eventKey={key}> 
            {label} {counts[key] !== null &&
                <Badge variant={badgeVariant}>
                    {counts[key]}
                </Badge>}</Nav.Link>
        </Nav.Item>
        );
    }

    return (
        <Nav variant="tabs" activeKey={selectedLevel}>
            {renderTab("project","Projects",counts.datafile,selectedLevel)}
            {renderTab("experiment","Experiments",counts.experiment,selectedLevel)}
            {renderTab("dataset","Datasets",counts.dataset,selectedLevel)}
            {renderTab("datafile","Datafiles",counts.datafile,selectedLevel)}
        </Nav>
    )
}

ResultTabs.propTypes = {
    counts: PropTypes.shape({
        project: PropTypes.number,
        experiment:PropTypes.number,
        dataset: PropTypes.number,
        datafile: PropTypes.number
    }),
    selectedLevel: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired
}


const NameColumn = {
    "project":"name",
    "experiment":"title",
    "dataset":"description",
    "datafile":"filename"
};

export function ResultRow({result,onSelect,isSelected}){
    const type = result.type,
        resultName = result[NameColumn[type]];
    return (
        <tr onClick={onSelect}>
            <td>
                {result.accessRights == "viewOnly" &&
                    <span aria-label="This item cannot be downloaded."><FiLock /></span>
                }
            </td>
            <td><a href={result.url}>{resultName}</a></td>
            <td>
                {result.accessRights != "viewOnly" && 
                    <span style={{paddingRight:"1em"}}>{result.safeFileSize}</span>
                }
                {result.accessRights == "some" &&
                    <span aria-label="Some files in this item cannot be downloaded."><FiPieChart /></span> 
                }
                {result.accessRights == "viewOnly" &&
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

export function PureResultList({results,selectedItem, onItemSelect, error, isLoading}){
    
    if (error) {
        return (<div>An error occurred. Please try searching again.</div>)
    }

    if (isLoading) {
        return (<div>Searching...</div>);
    }

    if (!results || 
        (Array.isArray(results) && results.length == 0)) {
            return (<div>No results.</div>)
    }


    const handleItemSelected = (id) => {
        onItemSelect(id);
    }

    return (
        <Table responsive striped hover bordered>
            <thead>
                <tr>
                    <th></th>
                    <th>Name</th>
                    <th>Size</th>
                </tr>
            </thead>
            <tbody>
            {
                results.map((result) => 
                    <ResultRow key={result.id} 
                        onSelect={handleItemSelected.bind(this,result.id)} 
                        result={result} 
                        isSelected={result.id === selectedItem} 
                    />)
            }
            </tbody>
        </Table>
    )
}

PureResultList.propTypes = {
    results: PropTypes.arrayOf(Object),
    error: PropTypes.object,
    isLoading: PropTypes.bool,
    selectedItem: PropTypes.string,
    onItemSelect: PropTypes.func
}

export function ResultList(props) {
    const [selected,onSelect] = useState(null)
    return (
        <PureResultList
            selectedItem={selected}
            onItemSelect={onSelect}
            {...props}
             />
    )
}

export function PureResultSection({resultSets, selected,
                                   onSelect, isLoading, error}){
    if (!resultSets){
        resultSets = {
            project: [],
            experiment: [],
            dataset: [],
            datafile: []
        }
    }
    const counts = {
        project: resultSets.project.length,
        experiment: resultSets.experiment.length,
        dataset: resultSets.dataset.length,
        datafile: resultSets.datafile.length
    };        

    const currentResultSet = resultSets[selected],
          currentCount = counts[selected];
    return (
        <>
            <ResultTabs counts={counts} selectedLevel={selected} onChange={onSelect} />
            <div role="tabpanel">
                {(!isLoading && !error) ?
                    <p>Showing {currentCount} results</p>
                    : null
                }
                <ResultList results={currentResultSet} isLoading={isLoading} error={error} />
            </div>
        </>
    )
}

export default function ResultSection() {
    const [selectedLevel, onSelect ] = useState('experiment'),
        searchInfo = useContext(SearchInfoContext);
    return (
        <PureResultSection
            resultSets={searchInfo.results}
            error={searchInfo.error}
            isLoading={searchInfo.isLoading}
            selected={selectedLevel}
            onSelect={onSelect}
        />
    )
}
