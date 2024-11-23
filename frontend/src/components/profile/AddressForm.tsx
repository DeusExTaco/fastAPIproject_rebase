import React from 'react';
import { Input, IconButton } from "@material-tailwind/react";
import { Trash2 } from 'lucide-react';
import { Address } from '../../types/profile';
import CustomCountrySelector from '@/components/custom/CustomCountrySelector';

type AddressField = Exclude<keyof Address, 'id' | 'user_id'>;

export interface AddressFormProps {
    readonly address: Address;
    readonly index: number;
    readonly onChange: (field: AddressField, value: string) => void;
    readonly onRemove: () => void;
    readonly isDeleted?: boolean;
}

const commonInputProps = {
    onPointerEnterCapture: () => {
    },
    onPointerLeaveCapture: () => {
    },
};

const AddressForm: React.FC<AddressFormProps> = ({
    address = {},
    index,
    onChange,
    onRemove,
    isDeleted = false
}) => {
    return (
        <div className={`p-4 border rounded-lg space-y-4 dark:border-gray-700 ${isDeleted ? 'opacity-50' : ''}`}>
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <h3 className="text-sm font-medium dark:text-white">Address {index + 1}</h3>
                    {isDeleted && (
                        <span className="text-xs text-red-500">(Pending Deletion)</span>
                    )}
                </div>
                <IconButton
                    variant="text"
                    color="red"
                    size="sm"
                    onClick={onRemove}
                    className="h-8 w-8"
                    placeholder={""}
                    {...commonInputProps}
                >
                    <Trash2 className="h-4 w-4"/>
                </IconButton>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="col-span-full">
                    <Input
                        label="Street"
                        color="blue"
                        value={address?.street ?? ''}
                        onChange={(e) => onChange('street', e.target.value)}
                        crossOrigin={undefined}
                        className="dark:text-white"
                        {...commonInputProps}
                    />
                </div>
                <Input
                    label="City"
                    color="blue"
                    value={address?.city ?? ''}
                    onChange={(e) => onChange('city', e.target.value)}
                    crossOrigin={undefined}
                    className="dark:text-white"
                    {...commonInputProps}
                />
                <Input
                    label="State"
                    color="blue"
                    value={address?.state ?? ''}
                    onChange={(e) => onChange('state', e.target.value)}
                    crossOrigin={undefined}
                    className="dark:text-white"
                    {...commonInputProps}
                />
                <Input
                    label="Postal Code"
                    color="blue"
                    value={address?.postal_code ?? ''}
                    onChange={(e) => onChange('postal_code', e.target.value)}
                    crossOrigin={undefined}
                    className="dark:text-white"
                    {...commonInputProps}
                />
                <CustomCountrySelector
                    value={address?.country ?? ''}
                    onChange={onChange}
                />
            </div>
        </div>
    );
};

export default AddressForm;