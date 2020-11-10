import React, { useMemo, useState } from 'react';
import PropTypes from "prop-types";
import Accordion from 'react-bootstrap/Accordion';
import Card from 'react-bootstrap/Card';
import { updateSchemaParameter, typeAttrSelector } from "../filterSlice";
import { useDispatch, useSelector } from "react-redux";
import CategoryFilter from '../category-filter/CategoryFilter';
import { runSearch } from '../../searchSlice';
import { mapTypeToFilter } from "../index";

// A hook for converting a hashmap of values into a list.
const useAsList = (jsObject = {}) => (
    useMemo(() => (
        Object.keys(jsObject)
            .map(key => jsObject[key]))
        , [jsObject])
);

const SchemaFilterList = ({ schema }) => {
    const { id: schemaId, type: schemaType, parameters } = schema,
        paramsAsList = useAsList(parameters),
        dispatch = useDispatch();

    return (<>
        {paramsAsList.map(
            param => {
                const setParamValue = (schemaId, parameterId, value) => {
                    dispatch(updateSchemaParameter({
                        schemaId,
                        parameterId,
                        value
                    }));
                    dispatch(runSearch());
                };
                return validatedFilter(param, dispatch, schemaId, setParamValue, "schema");
            }
        )}
    </>);

}

SchemaFilterList.propTypes = {
    schema: PropTypes.object.isRequired
}

export const PureTypeSchemaList = ({ value: schemaValue, onValueChange, options }) => {
    const { allIds: schemasAsList, byId: schemas } = options.schemas || { byId: {}, allIds: [] };
    let activeSchemas;
    if (!schemaValue) {
        // If there is no filter on what schemas to show, we show all of them.
        activeSchemas = schemasAsList;
    } else {
        activeSchemas = schemaValue.content;
    }

    const schemaList = useMemo(() => (
        // Return the schema list in format expected by CategoryFilter
        {
            allIds: schemasAsList,
            byId: schemasAsList.reduce((acc, schemaId) => {
                acc[schemaId] = {
                    label: schemas[schemaId].schema_name
                };
                return acc;
            }, {})
        }
    ), [schemasAsList, schemas]);

    if (schemasAsList.length === 0) {
        return null;
    }

    return (
        <section>
            <h3 className="h5">Schemas</h3>
            <CategoryFilter value={schemaValue} onValueChange={onValueChange} options={{
                checkAllByDefault: true,
                categories: schemaList
            }} />
            <Accordion>
                {schemasAsList.map((id) => {
                    const schema = schemas[id],
                        name = schema.schema_name;
                    if (!activeSchemas.includes(id)) {
                        // If schema is not selected, don't show filters for the schema.
                        return null;
                    }
                    return (
                        <Card key={name}>
                            <Card.Header>
                                <Accordion.Toggle as="button" className="btn btn-link" eventKey={id}>
                                    {name} filters
                                </Accordion.Toggle>
                            </Card.Header>
                            <Accordion.Collapse eventKey={id}>
                                <Card.Body>
                                    <SchemaFilterList schema={schema} />
                                </Card.Body>
                            </Accordion.Collapse>
                        </Card>
                    );
                })}
            </Accordion>
        </section>
    );
};

const TypeSchemaList = ({ typeId }) => {
    const allIds = useSelector(state => { return state.filters.typeSchemas[typeId] });
    const { byId } = useSelector(state => (state.filters.schemas)) || { byId: {} };
    const schemaValue = useSelector((state) => (
        typeAttrSelector(state.filters, typeId, "schema").value
    ));
    const onValueChange =
        (value) => {
            batch(() => {
                dispatch(updateActiveSchemas({ typeId, value }));
                dispatch(runSearch());
            });
        };

    const options = {
        schemas: {
            allIds,
            byId
        }
    }
    return (<PureTypeSchemaList value={schemaValue} onValueChange={onValueChange} options={options} />)
}

TypeSchemaList.propTypes = {
    typeId: PropTypes.string.isRequired
};

export default TypeSchemaList;

/**
 * Creates an filter with valid
 * @param {*} param 
 * @param {*} schemaId 
 * @param {*} valueSetter 
 * @param {*} filterType 
 */
export function validatedFilter(param, schemaId, valueSetter, filterType) {
    const { value, data_type: parameterType, full_name, id: parameterId } = param;
    const [isValid, setIsValid] = useState(true);

    const handleValueChange = (value) => {
        if (value.content === "valid") {
            setIsValid(true);
            valueSetter(schemaId, parameterId, value);
        } else {
            setIsValid(false);
        }
    };
    const ApplicableFilter = mapTypeToFilter(param.data_type);

    if (filterType === 'schema') {
    return (
        <section key={parameterId} className="single-schema-list__filter">
            <h5 className="single-schema-list__filter-label">{full_name}</h5>
            <ApplicableFilter
                id={schemaId + "." + parameterId}
                value={value}
                onValueChange={handleValueChange} />
            <ParentFilter isValid={isValid} />
            <hr />
        </section>
    );
    } else if (filterType === 'type') {
        return null;
    }
}
