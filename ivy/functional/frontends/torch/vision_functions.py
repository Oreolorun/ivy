import ivy


def pixel_shuffle(input, upscale_factor):
    input_shape = ivy.shape(input)

    ivy.assertions.check_equal(
        ivy.get_num_dims(input),
        4,
        message="pixel_shuffle expects 4D input, but got input with sizes "
                + str(input_shape),
    )
    b = input_shape[0]
    c = input_shape[1]
    h = input_shape[2]
    w = input_shape[3]
    upscale_factor_squared = upscale_factor * upscale_factor
    ivy.assertions.check_equal(
        c % upscale_factor_squared,
        0,
        message="pixel_shuffle expects input channel to be divisible by square "
                + "of upscale_factor, but got input with sizes "
                + str(input_shape)
                + ", upscale_factor="
                + str(upscale_factor)
                + ", and self.size(1)="
                + str(c)
                + " is not divisible by "
                + str(upscale_factor_squared),
    )
    oc = int(c / upscale_factor_squared)
    oh = h * upscale_factor
    ow = w * upscale_factor

    input_reshaped = ivy.reshape(input, (b, oc, upscale_factor, upscale_factor, h, w))
    return ivy.reshape(
        ivy.permute_dims(input_reshaped, (0, 1, 4, 2, 5, 3)), (b, oc, oh, ow)
    )


def pixel_unshuffle(input, downscale_factor):
    input_shape = ivy.shape(input)

    ivy.assertions.check_equal(
        ivy.get_num_dims(input),
        4,
        message=(
            f"pixel_unshuffle expects 4D input, "
            f"but got input with sizes {input_shape}"
        ),
    ),

    b = input_shape[0]
    c = input_shape[1]
    h = input_shape[2]
    w = input_shape[3]
    downscale_factor_squared = downscale_factor * downscale_factor

    ivy.assertions.check_equal(
        [h % downscale_factor, w % downscale_factor],
        [0, 0],  # Assert h % downscale_factor == 0 and w % downscale_factor == 0
        message=(
            f"pixel_unshuffle expects input height and width to be divisible by "
            f"downscale_factor, but got input with sizes {input_shape}"
            f", downscale_factor= {downscale_factor}"
            f", and either self.size(2)= {h}"
            f" or self.size(3)= {w}"
            f" is not divisible by {downscale_factor}"
        ),
    )
    oc = c * downscale_factor_squared
    oh = int(h / downscale_factor)
    ow = int(w / downscale_factor)

    input_reshaped = ivy.reshape(
        input, (b, c, oh, downscale_factor, ow, downscale_factor)
    )
    return ivy.reshape(
        ivy.permute_dims(input_reshaped, (0, 1, 3, 5, 2, 4)), (b, oc, oh, ow)
    )


def pad(input, padding, value=0):
    #  derive image shape
    input_shape = ivy.shape(input)

    # 4D input
    if len(input_shape) == 4:
        #  derive individual dimensions
        b = input_shape[0]
        c = input_shape[1]
        h = input_shape[2]
        w = input_shape[3]

        if len(padding) % 2 != 0:
            raise RuntimeError('Padding length must be divisible by 2')

        elif len(padding) > 4:
            raise RuntimeError('Padding length too large')

        elif len(padding) == 2:
            padded = ivy.ones((b, c, h, w + sum(padding))) * value

            for i in range(b):
                padded[i, :, :, padding[0]:-padding[1]] = input[i]
            return padded

        elif len(padding) == 4:
            padded = ivy.ones((b, c, h + sum(padding[:1:-1]),
                              w + sum(padding[:2]))) * value

            for i in range(b):
                padded[i, :, padding[-1]:-padding[-2], padding[0]:-padding[1]] = input[i]

            return padded

    # 3D input
    elif len(input_shape) == 3:

        #  derive individual dimensions
        c = input_shape[0]
        h = input_shape[1]
        w = input_shape[2]

        if len(padding) % 2 != 0:
            raise RuntimeError('Padding length must be divisible by 2')

        elif len(padding) > 4:
            raise RuntimeError('Padding length too large')

        elif len(padding) == 2:
            padded = ivy.ones((c, h, w + sum(padding))) * value

            for i in range(c):
                padded[i, :, padding[0]:-padding[1]] = input[i]

            return padded

        elif len(padding) == 4:
            padded = ivy.ones((c, h + sum(padding[:1:-1]),
                              w + sum(padding[:2]))) * value

            for i in range(c):
                padded[i, padding[-1]:-padding[-2], padding[0]:-padding[1]] = input[i]

            return padded

    # 2D input
    elif len(input_shape) == 2:

        #  derive individual dimensions
        h = input_shape[0]
        w = input_shape[1]

        if len(padding) % 2 != 0:
            raise RuntimeError('Padding length must be divisible by 2')

        elif len(padding) > 4:
            raise RuntimeError('Padding length too large')

        elif len(padding) == 2:
            padded = ivy.ones((h, w + sum(padding))) * value

            padded[:, padding[0]:-padding[1]] = input

            return padded

        elif len(padding) == 4:
            padded = ivy.ones((h + sum(padding[:1:-1]), w + sum(padding[:2]))) * value

            padded[padding[-1]:-padding[-2], padding[0]:-padding[1]] = input

            return padded
