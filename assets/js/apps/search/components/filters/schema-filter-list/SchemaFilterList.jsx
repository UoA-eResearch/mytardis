import React, { useState, useMemo } from 'react';
import { useDispatch } from 'react-redux'
import PropTypes from "prop-types";
import Accordion from 'react-bootstrap/Accordion';
import Form from 'react-bootstrap/Form';
import Card from 'react-bootstrap/Card';
import TextFilter from "../text-filter/TextFilter";
import { updateSchemaParameterFilter } from '../../searchSlice'
import './SchemaFilterList.css';

// A hook for converting a hashmap of values into a list.
const useAsList = (jsObject = {}) => (
    useMemo(() => (
        Object.keys(jsObject)
              .map(key => jsObject[key]))
    ,[jsObject])
);

const mapTypeToFilter = (type) => {
    switch (type) {
        case "STRING":
            return TextFilter;
        default:
            console.log("Filter not yet implemented");
            return null;
    }
}

const PureSchemaFilterList = ({value: schema, onValueChange}) => {
    const { id: schemaId, type: schemaType, parameters } = schema,
            paramsAsList = useAsList(parameters);

    return (<>
        {paramsAsList.map(
                param => {
                    const { value, full_name, id: parameterId } = param,
                          ApplicableFilter = mapTypeToFilter(param.data_type);
                    return (
                            <div className="single-schema-list__filter">
                                <h5 className="single-schema-list__filter-label">{full_name}</h5>
                                <ApplicableFilter value={value} onValueChange={onValueChange.bind(this, schemaType, schemaId, parameterId)} />
                                <hr />
                            </div>
                    );
                }
        )}
    </>);
    
}

PureSchemaFilterList.propTypes = {
    value: PropTypes.object.isRequired,
    onValueChange: PropTypes.func.isRequired
}

const SchemaFilterList = (props) => {
    const dispatch = useDispatch();
    const handleValueChange = (schemaType, schemaId, parameterId, filterValues) => {
        if (!Array.isArray(filterValues)){
            filterValues = [filterValues];
        }
        const changedValues = filterValues.map((value) => (
            Object.assign(value,{
                kind: "schemaParameter",
                target: [schemaId, parameterId]
            })
        ));
        dispatch(updateSchemaParameterFilter(changedValues));
    };
    return <PureSchemaFilterList {...props} onValueChange={handleValueChange} />
    // const handleValueChange = (schemaId,parameterId,)

}

const TypeSchemaList = ({ value, options, onValueChange }) => {
    // Generate a list of schemas based on the objects
    const schemasAsList = useAsList(options.schemas);
    const handleSchemaToggle = (schemaId,e) => {
        if (value.includes(schemaId)) {
            if (value.length == 1) {
                // Prevent switching off all schemas.
                return;
            }
            const newValue = value.filter(schema => schema !== schemaId);
            onValueChange(newValue);
        } else {
            const newValue = value.concat(schemaId);
            onValueChange(newValue);
        }
    }

    const getCheckValue = (id) => {
        return value.includes(id);
    }
    
    return (
        <div>
            <Form.Group>
                <Form.Label>Show me</Form.Label>
                {
                    
                    schemasAsList.map(
                        ({schema_name,id}) => (
                            <Form.Check 
                                key={id}
                                id={"schemaCheck-"+id}
                                type="checkbox" 
                                label={schema_name} 
                                checked={getCheckValue(id)} 
                                onChange={handleSchemaToggle.bind(this,id)} 
                            />
                        )
                    )
                }
            </Form.Group>
            <Accordion>
                {schemasAsList.map((schema) => {
                    const { id, schema_name } = schema;
                    if (!value.includes(id)) {
                        // If schema is not selected, don't show filters for the schema.
                        return null;
                    }
                    return (
                        <Card key={schema_name}>
                            <Accordion.Toggle as={Card.Header} eventKey={id}>
                                {schema_name}
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={id}>
                                <Card.Body>
                                    <SchemaFilterList value={schema} />
                                </Card.Body>
                            </Accordion.Collapse>
                        </Card>
                    );
                })}
            </Accordion>
        </div>
    );
};

TypeSchemaList.propTypes = {
    value: PropTypes.arrayOf(PropTypes.string).isRequired,
    options: PropTypes.shape({
        schemas: PropTypes.object
    }),
    onValueChange: PropTypes.func.isRequired
};

export default TypeSchemaList;