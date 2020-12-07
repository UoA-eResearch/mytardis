import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import InputGroup from 'react-bootstrap/InputGroup';
import FormControl from 'react-bootstrap/FormControl';
import Form from 'react-bootstrap/Form';
import PropTypes from 'prop-types';
import { batch, useDispatch, useSelector } from 'react-redux';
import { runSearch, updateSearchTerm, searchTermSelector } from './searchSlice';
import "./QuickSearchBox.css";

export function PureQuickSearchBox({searchTerm,onChange,onSubmit}) {
    const handleChange = (e) => {
        onChange(e.target.value);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(searchTerm);
    };

    return (
        <Form onSubmit={handleSubmit}>
            <FormControl className="quick-search-box__input" onChange={handleChange} value={searchTerm} aria-label="Quick find search input" placeholder="Find by title or description"></FormControl>
            <Button type="submit" aria-label="Quick find search button" variant="primary">Search</Button>
        </Form>
    )
}

PureQuickSearchBox.propTypes = {
    searchTerm: PropTypes.string,
    onChange: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired
}

const QuickSearchBox = ({typeId}) => {
    const searchTerm = useSelector(state => (searchTermSelector(state.search, typeId)));
    const [localSearchTerm, onTermChange] = useState(searchTerm);
    const dispatch = useDispatch();
    useEffect(() => {
        // Update the search term in the quick search box
        // when the term is externally updated (e.g. when 
        // the address contains a search term.)
        if (!searchTerm) {
            onTermChange("");
        } else {
            onTermChange(searchTerm);
        }
    }, [searchTerm]);
    return (
        <PureQuickSearchBox
            searchTerm={localSearchTerm}
            onChange={onTermChange}
            onSubmit={() => {
                const newSearchTerm = {};
                newSearchTerm[typeId] = localSearchTerm;
                batch(() => {
                    dispatch(updateSearchTerm({searchTerm: newSearchTerm}));
                    dispatch(runSearch());    
                });
            }}
        />
            
    );
};

QuickSearchBox.propTypes = {
    typeId: PropTypes.string.isRequired
};

export default QuickSearchBox;